import streamlit as st
import os
from rag_engine import ingest_documents, secure_rag_query

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Sovereign AI Chat",
    page_icon="🤖",
    layout="centered"
)

# Ensure data directory exists for uploads
DATA_DIR = "./data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# --- 2. SIDEBAR: DOCUMENT MANAGEMENT ---
with st.sidebar:
    st.title("📂 Document Vault")
    st.markdown("Upload PDFs to train your Sovereign AI.")
    
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file is not None:
        file_path = os.path.join(DATA_DIR, uploaded_file.name)
        
        # Save file to disk
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Trigger Ingestion
        with st.spinner(f"Ingesting {uploaded_file.name}..."):
            result = ingest_documents(file_path)
            st.success(result)

# --- 3. CHAT INTERFACE ---
st.title("🤖 Sovereign AI Assistant")
st.info("Directly connected to your private document vault. LlamaGuard 3 Firewall is ACTIVE.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Ask about your documents..."):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        with st.spinner("Analyzing and checking safety..."):
            # --- CALL THE SECURE FIREWALL WRAPPER ---
            response = secure_rag_query(prompt)
            st.markdown(response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
