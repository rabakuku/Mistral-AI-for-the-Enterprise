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

