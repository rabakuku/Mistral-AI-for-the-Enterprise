import os
import glob
import requests
import logging
from typing import List, Optional

# LangChain Imports (Updated for 2026 Modular Architecture)
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# --- CONFIGURATION & LOGGING ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SovereignRAG")

DB_PATH = "./chroma_db"
DATA_FOLDER = "./data"
COLLECTION_NAME = "enterprise_docs"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
VLLM_URL = "http://localhost:8000/v1/completions"

# --- CORE ENGINE INITIALIZATION ---

# 1. Initialize Embeddings (Downloads once to local cache)
logger.info(f"Initializing embeddings model: {EMBED_MODEL}")
embeddings = HuggingFaceEmbeddings(
    model_name=EMBED_MODEL,
    model_kwargs={'device': 'cuda'}  # Moves embedding work to the L4 GPU
)

# 2. Initialize Vector Store (Persistent)
# This will load existing data from DB_PATH if it exists
vector_db = Chroma(
    collection_name=COLLECTION_NAME,
    persist_directory=DB_PATH,
    embedding_function=embeddings
)

# --- ENGINE FUNCTIONS ---

def ingest_documents(file_path: str) -> str:
    """
    Processes a single PDF: Loads, Chunks, Embeds, and Stores.
    """
    try:
        if not os.path.exists(file_path):
            return f"Error: File {file_path} not found."

        logger.info(f"Ingesting: {file_path}")
        loader = PyPDFLoader(file_path)
        data = loader.load()

        # Recursive splitting preserves paragraph structure
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=150
        )
        chunks = text_splitter.split_documents(data)

        # Add to ChromaDB
        vector_db.add_documents(chunks)
        return f"Successfully ingested {os.path.basename(file_path)} ({len(chunks)} chunks)."

    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        return f"Failed to ingest {file_path}: {str(e)}"

def auto_scan_data_folder():
    """
    Scans the ./data folder. If the database is empty, it ingests all PDFs found.
    """
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
        return

    # Check current database size
    current_count = vector_db._collection.count()
    
    if current_count == 0:
        pdf_files = glob.glob(os.path.join(DATA_FOLDER, "*.pdf"))
        if pdf_files:
            logger.info(f"Database empty. Found {len(pdf_files)} PDFs in /data. Auto-ingesting...")
            for pdf in pdf_files:
                ingest_documents(pdf)
            logger.info("Auto-ingestion complete.")
        else:
            logger.warning("Database empty and no PDFs found in /data folder.")
    else:
        logger.info(f"Database ready with {current_count} document chunks.")

def ask_mistral_with_rag(query: str, k: int = 4) -> str:
    """
    The RAG Loop: 
    1. Search vector DB 
    2. Build context 
    3. Query Sovereign Mistral 7B
    """
    try:
        # 1. Retrieval
        docs = vector_db.similarity_search(query, k=k)
        if not docs:
            return "I do not have any relevant information in my private database to answer this."

        context = "\n---\n".join([d.page_content for d in docs])

        # 2. Grounded Prompt Engineering
        system_prompt = (
            "You are a Secure Enterprise AI. Answer ONLY based on the provided context. "
            "If the answer is not in the context, say 'Information not found in private records.'"
        )
        
        # vLLM prompt format for Mistral-Instruct
        formatted_prompt = f"<s>[INST] {system_prompt}\n\nCONTEXT:\n{context}\n\nQUESTION:\n{query} [/INST]"

        # 3. Local Inference (vLLM)
        response = requests.post(
            VLLM_URL,
            json={
                "model": "mistralai/Mistral-7B-Instruct-v0.3",
                "prompt": formatted_prompt,
                "max_tokens": 512,
                "temperature": 0.0,  # Strict grounding
                "stop": ["</s>"]
            },
            timeout=60
        )
        response.raise_for_status()
        
        return response.json()['choices'][0]['text'].strip()

    except Exception as e:
        logger.error(f"RAG Query Error: {e}")
        return f"System Error: Could not connect to the AI Engine. (Details: {str(e)})"

# --- INITIAL RUN ---
# Automatically scan for data whenever this script/app is loaded
auto_scan_data_folder()
