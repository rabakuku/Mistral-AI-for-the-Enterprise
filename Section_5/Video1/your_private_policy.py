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
