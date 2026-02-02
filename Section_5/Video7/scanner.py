import os
import sys
import pandas as pd
import giskard
import datetime
from giskard.llm.client.openai import OpenAIClient
from openai import OpenAI as LocalOpenAI
# Import the updated engine and vector_db
from rag_engine import ask_mistral_with_rag, vector_db

# --- 1. CONFIGURATION ---
REPORT_DIR = "/sovereign-ai/reports"
if not os.path.exists(REPORT_DIR):
    os.makedirs(REPORT_DIR)

# --- 2. CONFIGURE LOCAL EVALUATOR (THE JUDGE) ---
local_client = LocalOpenAI(
    base_url="http://localhost:8000/v1", 
    api_key="sovereign-key" 
)

# FIXED: New Giskard 3.x syntax for setting the client
giskard.llm.set_llm_api("openai")
giskard.llm.set_default_client(
    OpenAIClient(model="mistralai/Mistral-7B-Instruct-v0.3", client=local_client)
)

def run_giskard_audit(choice):
    # --- 3. WRAP YOUR MODEL ---
    # FIXED: This function now retrieves the context BEFORE calling the engine
    def model_predict(df: pd.DataFrame):
        responses = []
        for q in df["question"]:
            query_str = str(q)
            # Perform a local similarity search for each test question
            docs = vector_db.similarity_search(query_str, k=4)
            context = "\n---\n".join([d.page_content for d in docs])
            
            # Pass BOTH query and context to the updated engine
            res = ask_mistral_with_rag(query_str, context)
            responses.append(res)
        return responses

    giskard_model = giskard.Model(
        model=model_predict,
        model_type="text_generation",
        name="Sovereign_Mistral_RAG",
        description="Internal policy assistant for SovereignCorp.",
        feature_names=["question"]
    )

    # --- 4. PREPARE KNOWLEDGE BASE ---
    docs = vector_db.get()
    if not docs['documents']:
        print("[-] ❌ Error: No documents found in ChromaDB. Ingest data first.")
        return

    knowledge_base_df = pd.DataFrame({"question": docs['documents'][:10]}) # Sample for speed
    wrapped_dataset = giskard.Dataset(df=knowledge_base_df, name="PolicyData", target=None)

    # --- 5. SELECTIVE AUDIT LOGIC ---
    audit_map = {
        "1": (["hallucination"], "hallucination"),
        "2": (["jailbreak", "prompt_injection"], "injection"),
        "3": (["information_disclosure"], "disclosure"),
        "4": (None, "full_audit")
    }
    
    selected_tags, type_label = audit_map.get(choice, (None, "manual_scan"))

    print(f"\n🚀 Starting {type_label.upper()} scan using LOCAL evaluator...")

    # --- 6. RUN SCAN ---
    scan_results = giskard.scan(
        giskard_model, 
        dataset=wrapped_dataset, 
        only=selected_tags,
        max_issues_per_detector=5 
    )

    # --- 7. SAVE REPORT ---
    date_str = datetime.datetime.now().strftime("%m.%d.%Y")
    filename = f"{type_label}_{date_str}.html"
    filepath = os.path.join(REPORT_DIR, filename)
    
    scan_results.to_html(filepath)
    print("-" * 40)
    print(f"✅ Success! Report saved: {filepath}")
    print("📈 View it now in your Widescreen Command Center (Port 8502).")
    print("-" * 40)

if __name__ == "__main__":
    print("\n--- 🛡️ Sovereign AI: CLI Security Manager ---")
    
    if len(sys.argv) > 1:
        user_choice = sys.argv[1]
    else:
        print("1. Hallucination (Strict Grounding Test)")
        print("2. Jailbreaking & Prompt Injection")
        print("3. Information Disclosure")
        print("4. Full System Audit")
        user_choice = input("\n[?] Which vulnerability would you like to scan for? (1-4): ")
    
    if user_choice in ["1", "2", "3", "4"]:
        run_giskard_audit(user_choice)
    else:
        print("[-] Invalid selection. Exiting.")
