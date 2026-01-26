In this Video, we transition from building the "Brain" to building the "Library." 🏛️ We are creating the **RAG (Retrieval-Augmented Generation)** system that allows our Mistral model to "read" your private PDF documents and answer questions based solely on your data.

## 📂 Phase 1: Install Modules

To get your **Sovereign AI** environment ready, you need to install the libraries that power the vector database, the PDF processing, and the web interface.

Since you are using a professional Conda environment (`vllm-env`), run this one-liner to install all required dependencies at once:

```javascript
# 1. Enter your environment
conda activate vllm-env

# 2. Install python Libraries 
pip install chromadb langchain langchain-community langchain-huggingface langchain-chroma pypdf sentence-transformers requests streamlit

```




### **What is being installed?** 📦

| **Library** | **Role in Your Engine** |
| **`chromadb`&#32;&&#32;`langchain-chroma`** | The "Vault" where your document vectors are stored securely. |
| **`langchain-huggingface`** | The bridge that allows your **NVIDIA L4** to run the embedding models locally. |
| **`pypdf`** | The "Reader" that extracts raw text from your uploaded policy documents. |
| **`sentence-transformers`** | The math engine that converts sentences into searchable numbers (vectors). |
| **`streamlit`** | The framework that builds your professional 🛡️ Sovereign AI web dashboard. |
|  |  |




### **Pro-Tip: Verification** ✅

After the installation finishes, you can verify that the key components are correctly linked to your Python environment by running:

Bash

```javascript
python3 -c "import langchain_chroma; import streamlit; print('🚀 Environment Ready!')"

```




### 🧠 What do these scripts do?

The `rag_engine.py` script serves as the core intelligence hub, responsible for scanning your private folders and converting text into mathematical vectors for the database. By utilizing a "local-first" embedding model, it ensures your data never leaves the VM while it chunks long documents into digestible pieces for the AI. The `app.py` script provides a sleek, user-friendly Streamlit interface, allowing non-technical users to upload new PDFs and interact with the AI via a familiar chat box. Together, these scripts create a "walled garden" where your enterprise data stays private while remaining fully searchable by the Mistral 7B engine.

## 📂 Phase 2: Professional Project Structure

Organization is the hallmark of a professional AI Engineer. 🛠️ Before writing code, we must ensure our folder structure is scannable and ready for deployment.

```javascript
# 1. Create our script placeholders
nano rag_engine.py 
nano app.py

```




## 🏗️ Phase 3: The Combined RAG Engine (`rag_engine.py`)

This file is the "Logic Layer." 🧠 It handles the heavy lifting: reading PDFs, splitting them into paragraphs, and talking to your **vLLM** server.

Python

```javascript
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

```




## 🎨 Phase 4: The Streamlit Interface (`app.py`)

This is the "Presentation Layer." 🖥️ It provides a beautiful, web-based UI so you can interact with your AI without using the terminal.

```javascript
import streamlit as st
from rag_engine import ingest_documents, ask_mistral_with_rag
import os

st.set_page_config(page_title="Sovereign AI", page_icon="🛡️")
st.title("🛡️ Sovereign AI Engine")

# Sidebar for Document Management
with st.sidebar:
    st.header("Document Management")
    uploaded_file = st.file_uploader("Upload Policy PDF", type="pdf")
    if st.button("Ingest Document"):
        if uploaded_file:
            with open("temp.pdf", "wb") as f:
                f.write(uploaded_file.getbuffer())
            with st.spinner("Processing..."):
                msg = ingest_documents("temp.pdf")
                st.success(msg)
            os.remove("temp.pdf")
        else:
            st.error("Please upload a file first.")

# Main Chat Interface
query = st.text_input("Query the Database:", placeholder="e.g., What are the security requirements?")

if st.button("Search"):
    if query:
        with st.spinner("Searching private documents..."):
            answer = ask_mistral_with_rag(query)
            st.markdown("### Response:")
            st.info(answer)

```




### **Pro-Tip: The "Golden Rule" of RAG** 🎓

Notice the `temperature: 0.0` in the `rag_engine.py`. For production enterprise data, we do not want the AI to be "creative." We want it to be a **fact-checking machine**. Setting temperature to zero ensures the AI sticks strictly to the PDF text provided!


