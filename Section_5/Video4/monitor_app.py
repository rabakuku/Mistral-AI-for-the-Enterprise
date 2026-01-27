import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import subprocess
import time

# --- 1. SECURE SECRETS LOADING ---
try:
    with open('secrets.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
    
    # DYNAMIC DETECTION: Get the first username found in the file
    detected_username = list(config['credentials']['usernames'].keys())[0]
except (FileNotFoundError, IndexError, KeyError):
    st.error("Credential file missing! Run 'update_secrets.py' first.")
    st.stop()

# --- 2. INITIALIZE AUTHENTICATOR ---
authenticator = stauth.Authenticate(
    config['credentials'],
    'sovereign_cookie',
    'auth_key',
    cookie_expiry_days=1
)

# --- 3. STEALTH LOGIN LOGIC ---
# Pre-fill the session state with the DETECTED username
if 'username' not in st.session_state:
    st.session_state['username'] = detected_username 

# CSS Hack to hide the username field
st.markdown("""
    <style>
    div[data-testid="stTextInput"] > label:contains("Username") ,
    div[data-testid="stTextInput"]:has(label:contains("Username")) {
        display: none;
    }
    </style>
""", unsafe_allow_html=True)

# FIX: In v0.4.x, the first argument is 'location'. 
# We use keyword arguments to be 100% safe.
authenticator.login(location='main')

# --- 4. CHECK AUTHENTICATION STATUS ---
# The status is now stored directly in st.session_state
if st.session_state.get('authentication_status'):
    # Success! Clear the login UI and show the dashboard
    st.title("🛡️ Sovereign AI Command Center")
    st.info(f"Session Active: {st.session_state['name']}")

    def get_logs():
        # Grabbing logs from the system
        cmd = "sudo journalctl -u sovereign-ui.service -u vllm.service -n 50 --no-hostname --output=short-precise"
        return subprocess.run(cmd.split(), capture_output=True, text=True).stdout

    st.code(get_logs(), language="bash")
    
    # Auto-Refresh loop
    time.sleep(5)
    st.rerun()

elif st.session_state.get('authentication_status') is False:
    st.error('Access Denied: Invalid Key')
else:
    # This state means the user hasn't tried to log in yet
    st.warning('Please enter your Access Key to continue.')
