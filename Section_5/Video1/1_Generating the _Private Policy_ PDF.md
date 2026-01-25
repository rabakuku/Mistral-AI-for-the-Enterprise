### **Note: The Sovereign Directory Structure** 🗺️

By the end of this lab, your students' project should look exactly like this. Consistency is key to a successful deployment!

```javascript
sovereign-ai/
├── data/               # 📂 Drop your PDFs here
├── chroma_db/          # 🏦 Persistent database folder (auto-created later)
├── rag_engine.py       # 🧠 Core logic (Ingestion & Search)
├── app.py              # 🎨 Streamlit User Interface
└── sovereign_ai.service # ⚙️ System service file

```

## 🎬  Preparing the Vector Database (ChromaDB)

Now that we have a file, we need a place to store its "meaning." 🏦 A **Vector Database** doesn't store words; it stores numbers that represent the *concepts* within your documents.

### **Step 1: Install RAG Dependencies** 🛠️

We need to equip our environment with the tools required for **Retrieval-Augmented Generation (RAG)**.

```javascript
# Ensure you are still in /sovereign-ai/ and the vllm-env is active
pip install chromadb langchain langchain-mistralai pypdf sentence-transformers

```




### 🧩 **The "Big Three" Components Explained** 🎓

| **Library** | **Role in Your Engine** |
| **`chromadb`** | 🏦 **The Vault:** Our lightweight, open-source vector database that holds your data securely. |
| **`sentence-transformers`** | 🔢 **The Translator:** The "Embedding Model" that turns human sentences into mathematical vectors. |
| **`pypdf`** | 📖 **The Reader:** The tool that "cracks open" your PDF files so the AI can read the text inside. |




### 

### 📑 Lab: Creating Your Training Data & Vector Storage

In this section, we transition from building the "Engine" to building the "Knowledge." 🧠 We will create our own private company document and set up the **Vector Database** that will allow our AI to search through it securely.




### 📄 What do**es** the script do?

The first script serves as a document generator that programmatically builds a professional PDF containing mock "SovereignCorp" security policies. This provides your students with a clean, standardized piece of data to use for testing the RAG system's retrieval accuracy. 

## 🏗️ Phase 1: Generating the "Private Policy" PDF

Since we are building a Sovereign system, we need data! 📂 Run this script to create a mock corporate policy that we will later "teach" to our Mistral model.

### **Step 1: Set Up the Project Structure** 📁

We want to keep our workspace organized like a pro.

Bash

```javascript
# 1. Elevate to root and move to the base directory
sudo su 
cd /

# 2. Refresh your environment
conda activate vllm-env
conda deactivate
conda activate vllm-env

# 3. Create the project folder and the data directory
mkdir -p sovereign-ai/data
cd sovereign-ai/
mkdir data
mkdir chroma_db
cd data
# 4. Install the PDF generation library
pip install fpdf

```

### **Step 2: Create the Policy Generator** ✍️

Run `nano your_private_policy.py`, paste the code below, then save and exit (`Ctrl+O`, `Enter`, `Ctrl+X`).

```javascript
from fpdf import FPDF

class PolicyPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'SovereignCorp Internal AI & Data Policy', 0, 1, 'C')
        self.ln(10)

pdf = PolicyPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)

# Page 1: General Conduct
pdf.cell(200, 10, txt="Section 1: Data Handling Protocols", ln=True)
pdf.multi_cell(0, 10, txt=(
    "1.1. All sensitive company data must be processed within the local VPC. "
    "1.2. Under no circumstances should employee records be uploaded to public LLM APIs. "
    "1.3. Encryption at rest is mandatory for all vector databases stored on local SSDs. "
    "1.4. The 'Project Mistral' team is the only authorized group to modify the system prompt."
))

# Page 2: Security & Compliance
pdf.add_page()
pdf.cell(200, 10, txt="Section 2: Security Compliance", ln=True)
pdf.multi_cell(0, 10, txt=(
    "2.1. System audits will be performed weekly by the Sovereignty Architect. "
    "2.2. Any detected hallucinations in production must be reported via the internal Jira ticket system. "
    "2.3. The designated admin for this engine is 'Admin_User_01'. "
    "2.4. Unauthorized access to the ChromaDB directory is a Grade 4 security violation."
))

pdf.output("data/your_private_policy.pdf")
print("PDF created successfully in the data/ folder.")

```

### **Step 3: Run the Generator** ⚡

Bash

```javascript
python3 your_private_policy.py

```




## 