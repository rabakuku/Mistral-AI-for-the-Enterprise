import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import subprocess
import time
import os

# --- 1. CORE WIDESCREEN CONFIGURATION ---
st.set_page_config(
    page_title="Sovereign AI Command Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. LOAD CONFIG & INITIALIZE AUTHENTICATOR ---
# We move this to the top so 'authenticator' exists for the rest of the script
with open('/sovereign-ai/secrets.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'], 
    'sovereign_cookie', 
    'auth_key',
    cookie_expiry_days=30
)

# --- 3. LOGIN LOGIC ---
# In streamlit-authenticator v0.3.x+, .login() updates session state directly.
# We no longer need to capture a tuple like (name, authentication_status, username).
authenticator.login(location='main')

# --- 4. ACCESS CONTROL ---
if st.session_state.get('authentication_status'):
    # AUTHENTICATED: Display the Dashboard
    st.title("🛡️ Sovereign AI Command Center")
    
    # Optional: Hide Username UI via CSS
    st.markdown("<style>div[data-testid='stTextInput'] > label:contains('Username') {display: none;}</style>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📟 System Logs", "🕵️ Security Vault"])

    with tab1:
        st.subheader("Live Service Logs")
        def get_logs():
            # Grabbing logs from both the UI and the Inference engine
            cmd = "sudo journalctl -u sovereign-ui.service -u vllm.service -n 50 --no-hostname --output=short-precise"
            return subprocess.run(cmd.split(), capture_output=True, text=True).stdout
        
        st.code(get_logs(), language="bash")
        if st.button("Refresh Logs"): 
            st.rerun()

    with tab2:
        st.subheader("🕵️ Automated Vulnerability Reports")
        REPORT_DIR = "/sovereign-ai/reports"
        
        if os.path.exists(REPORT_DIR):
            reports = sorted([f for f in os.listdir(REPORT_DIR) if f.endswith(".html")], reverse=True)
            if reports:
                selected_report = st.selectbox("View CLI-Generated Report", reports)
                report_path = os.path.join(REPORT_DIR, selected_report)
                with open(report_path, 'r') as f:
                    st.components.v1.html(f.read(), height=1200, scrolling=True)
            else:
                st.info("No reports found. Run 'python3 scanner.py' in the terminal.")
        else:
            st.error("Report directory missing.")

    # Sidebar Logout
    authenticator.logout('Logout', 'sidebar')
    
    # Auto-refresh logic (optional, use with caution)
    # time.sleep(10)
    # st.rerun()

elif st.session_state.get('authentication_status') is False:
    st.error('Username/password is incorrect')

elif st.session_state.get('authentication_status') is None:
    st.warning('Please enter your username and password')
