import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import subprocess
import time

# --- 1. SECURE SECRETS LOADING ---
# We load the file and automatically find the current username
try:
    with open('secrets.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
    
    # DYNAMIC DETECTION: Get the first username found in the file
    # This replaces the hardcoded 'admin_user' from before!
    detected_username = list(config['credentials']['usernames'].keys())[0]
except (FileNotFoundError, IndexError, KeyError):
    st.error("Credential file missing or corrupted! Run 'update_secrets.py' first.")
    st.stop()

# --- 2. INITIALIZE AUTHENTICATOR ---
authenticator = stauth.Authenticate(
    config['credentials'],
    'sovereign_cookie',
    'auth_key',
    cookie_expiry_days=1
)

# --- 3. STEALTH LOGIN LOGIC ---
# Hide the username field via CSS
st.markdown("""
    <style>
    div[data-testid="stTextInput"] > label:contains("Username") ,
    div[data-testid="stTextInput"]:has(label:contains("Username")) {
        display: none;
    }
    </style>
""", unsafe_allow_html=True)

# Pre-fill the session state with the DETECTED username
if 'username' not in st.session_state:
    st.session_state['username'] = detected_username 

login_placeholder = st.empty()

with login_placeholder.container():
    # The user only sees the 'Access Key' (password) input
    name, authentication_status, username = authenticator.login('Enter Access Key', 'main')

if authentication_status:
    login_placeholder.empty() # Erase the login box upon success
    
    # --- 4. COMMAND CENTER DASHBOARD ---
    st.title("🛡️ Sovereign AI Command Center")
    st.info(f"Session Active: {name}")

    def get_logs():
        # Merged journalctl stream for UI and vLLM
        cmd = "sudo journalctl -u sovereign-ui.service -u vllm.service -n 50 --no-hostname --output=short-precise"
        return subprocess.run(cmd.split(), capture_output=True, text=True).stdout

    st.code(get_logs(), language="bash")
    
    # Auto-Refresh to maintain the 'Live' feeling
    time.sleep(5)
    st.rerun()

elif authentication_status == False:
    st.error('Access Denied: Invalid Key')
