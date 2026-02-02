import os
import glob
import requests
import logging
import json
from typing import List, Optional

# LangChain Imports (2026 Modular Architecture)
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# --- CONFIGURATION & LOGGING ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SovereignRAG")

DB_PATH = "/sovereign-ai/chroma_db"
DATA_FOLDER = "/sovereign-ai/data"
COLLECTION_NAME = "enterprise_docs"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Local vLLM Endpoints
VLLM_URL = "http://localhost:8000/v1/completions"
MODEL_MISTRAL = "mistralai/Mistral-7B-Instruct-v0.3"
MODEL_LLAMAGUARD = "meta-llama/Llama-Guard-3-8B"

# --- CORE ENGINE INITIALIZATION ---

logger.info(f"Initializing embeddings model: {EMBED_MODEL}")
embeddings = HuggingFaceEmbeddings(
    model_name=EMBED_MODEL,
    model_kwargs={'device': 'cuda'}  
)

vector_db = Chroma(
    collection_name=COLLECTION_NAME,
    persist_directory=DB_PATH,
    embedding_function=embeddings
)

# --- 🛡️ INTERNAL SECURITY GUARDRAILS (LlamaGuard 3) ---

def check_safety(text: str, role: str = "user") -> (bool, str):
    """
    Directly queries LlamaGuard 3 using the official MLCommons Taxonomy.
    """
    taxonomy = """
S1: Violent Crimes. 
S2: Non-Violent Crimes. 
S3: Sex-Related Crimes. 
S4: Child Sexual Exploitation. 
S5: Defamation. 
S6: Specialized Advice. 
S7: Privacy. 
S8: Intellectual Property. 
S9: Indiscriminate Weapons. 
S10: Hate. 
S11: Suicide & Self-Harm. 
S12: Sexual Content. 
S13: Elections.
"""
    formatted_prompt = f"""<|begin_of_text|><|start_header_id|>user<|end_header_id|>

Task: Check if there is unsafe content in the {role} message in accordance with our safety policy with the below categories.

<BEGIN UNSAFE CONTENT CATEGORIES>
{taxonomy}
<END UNSAFE CONTENT CATEGORIES>

<BEGIN CONVERSATION>
{"User" if role == "user" else "Agent"}: {text}
<END CONVERSATION>

Provide your safety assessment for {role} in the above conversation:
- First line must read 'safe' or 'unsafe'.
- If unsafe, a second line must include a comma-separated list of violated categories.<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""

    payload = {
        "model": MODEL_LLAMAGUARD,
        "prompt": formatted_prompt,
        "temperature": 0.0,
        "max_tokens": 10
    }

    try:
        response = requests.post(VLLM_URL, json=payload, timeout=10)
        response.raise_for_status()
        prediction = response.json()['choices'][0]['text'].strip().lower()
        
        if "unsafe" in prediction:
            return False, prediction
        return True, "safe"
    except Exception as e:
        logger.error(f"Guardrail Error: {e}")
        return False, "guardrail_service_error"

# --- INGESTION FUNCTIONS ---

def ingest_documents(file_path: str) -> str:
    """Processes a single PDF: Loads, Chunks, Embeds, and Stores."""
    try:
        if not os.path.exists(file_path):
            return f"Error: File {file_path} not found."

        logger.info(f"Ingesting: {file_path}")
        loader = PyPDFLoader(file_path)
        data = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=150
        )
        chunks = text_splitter.split_documents(data)

        vector_db.add_documents(chunks)
        return f"Successfully ingested {os.path.basename(file_path)} ({len(chunks)} chunks)."
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        return f"Failed to ingest {file_path}: {str(e)}"

def auto_scan_data_folder():
    """Auto-scans /data folder on startup."""
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
        return

    current_count = vector_db._collection.count()
    if current_count == 0:
        pdf_files = glob.glob(os.path.join(DATA_FOLDER, "*.pdf"))
        if pdf_files:
            logger.info(f"DB empty. Ingesting {len(pdf_files)} PDFs...")
            for pdf in pdf_files:
                ingest_documents(pdf)
    else:
        logger.info(f"Database ready with {current_count} chunks.")

# --- RAG & FIREWALL LOGIC ---

def ask_mistral_with_rag(query: str, k: int = 4) -> str:
    """Core RAG logic: Retrieve context and query Mistral."""
    try:
        docs = vector_db.similarity_search(query, k=k)
        if not docs:
            return "Information not found in private records."

        context = "\n---\n".join([d.page_content for d in docs])

        system_prompt = (
            "You are a Secure Enterprise AI. Answer ONLY based on the provided context. "
            "If the answer is not in the context, say 'Information not found in private records.'"
        )
        
        formatted_prompt = f"<s>[INST] {system_prompt}\n\nCONTEXT:\n{context}\n\nQUESTION:\n{query} [/INST]"

        response = requests.post(
            VLLM_URL,
            json={
                "model": MODEL_MISTRAL,
                "prompt": formatted_prompt,
                "max_tokens": 512,
                "temperature": 0.0,
                "stop": ["</s>"]
            },
            timeout=60
        )
        response.raise_for_status()
        return response.json()['choices'][0]['text'].strip()

    except Exception as e:
        logger.error(f"RAG Engine Error: {e}")
        return "System Error: Inference connection failed."

def secure_rag_query(user_query: str) -> str:
    """
    Sovereign Firewall: Wraps the RAG engine in LlamaGuard 3 checks.
    """
    is_safe_in, reason_in = check_safety(user_query, role="user")
    if not is_safe_in:
        logger.warning(f"BLOCKED INPUT: {reason_in}")
        return f"🛡️ Sovereign Shield: Input Blocked. Policy Violation: {reason_in}"

    answer = ask_mistral_with_rag(user_query)

    is_safe_out, reason_out = check_safety(answer, role="assistant")
    if not is_safe_out:
        logger.warning(f"BLOCKED OUTPUT: {reason_out}")
        return "🛡️ Sovereign Shield: Response Blocked. Safety violation detected."

    return answer

# --- BOOTSTRAP ---
auto_scan_data_folder()
