import requests

LLAMAGUARD_URL = "http://localhost:8000/v1/completions" # Use completions for direct prompt control
MODEL_NAME = "meta-llama/Llama-Guard-3-8B"

def check_safety(text, role="user"):
    # The "Secret Sauce": The Llama Guard 3 Prompt Template
    # This tells the model exactly which categories to audit.
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
    
    # We format the prompt exactly as Llama Guard 3 expects
    # Note: 'role' determines if we are checking the User or the Assistant
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
        "model": MODEL_NAME,
        "prompt": formatted_prompt, # We use the direct prompt
        "temperature": 0.0,
        "max_tokens": 10
    }

    try:
        response = requests.post(LLAMAGUARD_URL, json=payload, timeout=5)
        response.raise_for_status()
        
        prediction = response.json()['choices'][0]['text'].strip().lower()
        
        if "unsafe" in prediction:
            return False, prediction 
        return True, "safe"
        
    except Exception as e:
        print(f"[-] Guardrail Error: {e}")
        return False, "guardrail_error"
