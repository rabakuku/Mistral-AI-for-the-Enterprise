import os
import glob
import requests
import logging
import json
import re
import pandas as pd
from datetime import datetime
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
LOG_FILE = "/sovereign-ai/security_events.csv"
COLLECTION_NAME = "enterprise_docs"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Local vLLM Endpoints
VLLM_URL = "http://localhost:8000/v1/completions"
MODEL_MISTRAL = "mistralai/Mistral-7B-Instruct-v0.3"
MODEL_LLAMAGUARD = "meta-llama/Llama-Guard-3-8B"

# --- CORE ENGINE INITIALIZATION ---
embeddings = HuggingFaceEmbeddings(
    model_name=EMBED_MODEL,
    model_kwargs={'device': 'cuda'}  
)

vector_db = Chroma(
    collection_name=COLLECTION_NAME,
    persist_directory=DB_PATH,
    embedding_function=embeddings
)

# --- 📊 SECURITY LOGGING ---

def log_security_event(user_id: str, category: str, prompt: str):
    """Logs blocked attempts to a central CSV for the Leaderboard."""
    new_event = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_id": user_id,
        "category": category,
        "prompt_snippet": prompt[:50].replace(",", " ") + "..."
    }
    df = pd.DataFrame([new_event])
    df.to_csv(LOG_FILE, mode='a', header=not os.path.exists(LOG_FILE), index=False)
    logger.warning(f"SECURITY EVENT LOGGED: {category} by {user_id}")

# --- 🛡️ ADVANCED SOVEREIGN SHIELD LOGIC ---

def detect_jailbreak_patterns(text: str) -> bool:
    patterns = [r"ignore all previous instructions", r"act as DAN", r"Developer Mode", r"DUDE"]
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

def check_safety(text: str, role: str = "user") -> (bool, str):
    taxonomy = "S1: Violence, S2: Crimes, S11: Jailbreaking, S12: Sexual Content"
    formatted_prompt = f"""<|begin_of_text|><|start_header_id|>user<|end_header_id|>
Task: Check safety. Pay attention to S11: Jailbreaking.
<BEGIN UNSAFE CONTENT CATEGORIES>
{taxonomy}
<END UNSAFE CONTENT CATEGORIES>
<BEGIN CONVERSATION>
{"User" if role == "user" else "Agent"}: {text}
<END CONVERSATION>
Provide assessment: safe/unsafe.<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""

    try:
        response = requests.post(VLLM_URL, json={
            "model": MODEL_LLAMAGUARD, "prompt": formatted_prompt, "temperature": 0.0, "max_tokens": 10
        }, timeout=10)
        prediction = response.json()['choices'][0]['text'].strip().lower()
        return ("unsafe" not in prediction), prediction
    except Exception as e:
        return False, "service_error"

# --- RAG CORE & SECURE WRAPPER ---

def ask_mistral_with_rag(query: str, context: str) -> str:
    system_prompt = "You are a Secure AI. Answer ONLY based on context."
    formatted_prompt = f"<s>[INST] {system_prompt}\n\nCONTEXT:\n{context}\n\nQUESTION:\n{query} [/INST]"
    response = requests.post(VLLM_URL, json={
        "model": MODEL_MISTRAL, "prompt": formatted_prompt, "max_tokens": 512, "temperature": 0.0
    }, timeout=60)
    return response.json()['choices'][0]['text'].strip()

def secure_rag_query(user_query: str, user_id: str = "anonymous_attacker") -> str:
    # PASS 1: Heuristic
    if detect_jailbreak_patterns(user_query):
        log_security_event(user_id, "Heuristic: Jailbreak Pattern", user_query)
        return "🛡️ Sovereign Shield: Jailbreak Attempt Blocked."

    # PASS 2: LlamaGuard Input
    is_safe_in, reason_in = check_safety(user_query, role="user")
    if not is_safe_in:
        log_security_event(user_id, f"LlamaGuard: {reason_in}", user_query)
        return f"🛡️ Sovereign Shield: Input Blocked."

    # PASS 3: Process & Check Final Output
    docs = vector_db.similarity_search(user_query, k=4)
    context = "\n---\n".join([d.page_content for d in docs])
    answer = ask_mistral_with_rag(user_query, context)
    
    is_safe_out, reason_out = check_safety(answer, role="assistant")
    if not is_safe_out:
        log_security_event(user_id, f"LlamaGuard Output: {reason_out}", user_query)
        return "🛡️ Sovereign Shield: Safety Violation detected."
    
    return answer

# --- INGESTION & SCAN ---
def ingest_documents(file_path: str):
    # (Existing logic)
    pass

def auto_scan_data_folder():
    # (Existing logic)
    pass

auto_scan_data_folder()
