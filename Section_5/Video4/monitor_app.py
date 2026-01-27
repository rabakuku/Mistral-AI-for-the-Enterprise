import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import subprocess
import time
import os

# --- 1. CORE WIDESCREEN CONFIGURATION ---
# layout="wide" forces the app to use the full browser width
st.set_page_config(
    page_title="Sovereign AI Command Center",
    page_icon="🛡️",
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- 2. INITIALIZE PLACEHOLDERS ---
login_placeholder = st.empty()

# --- 3. SECURE SECRETS LOADING ---
try:
    with open('/sovereign-ai/secrets.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
    
    # Auto-detect the current username from the YAML
    detected_username = list(config['credentials']['usernames'].keys())[0]
except (FileNotFoundError, IndexError, KeyError):
    st.error("Credential file missing! Run 'update_secrets.py' first.")
    st.stop()

# --- 4. INITIALIZE AUTHENTICATOR ---
authenticator = stauth.Authenticate(
    config['credentials'],
    'sovereign_cookie',
    'auth_key',
    cookie_expiry_days=1
)

# --- 5. STEALTH LOGIN UI ---
if 'username' not in st.session_state:
    st.session_state['username'] = detected_username 

# CSS Hack to hide the username input for a "Password-Only" experience
st.markdown("""
    <style>
    div[data-testid="stTextInput"] > label:contains("Username") ,
    div[data-testid="stTextInput"]:has(label:contains("Username")) {
        display: none;
    }
    </style>
""", unsafe_allow_html=True)

with login_placeholder.container():
    authenticator.login(location='main')

# --- 6. DASHBOARD LOGIC (AUTHENTICATED) ---
if st.session_state.get('authentication_status'):
    login_placeholder.empty() 
    
    st.title("🛡️ Sovereign AI Command Center")
    st.info(f"Session Active: {st.session_state['name']}")

    # Tabbed Navigation
    tab1, tab2 = st.tabs(["📟 System Logs", "🕵️ Security Vault"])

    with tab1:
        st.subheader("Live System Telemetry")
        def get_logs():
            cmd = "sudo journalctl -u sovereign-ui.service -u vllm.service -n 50 --no-hostname --output=short-precise"
            return subprocess.run(cmd.split(), capture_output=True, text=True).stdout
        st.code(get_logs(), language="bash")
        if st.button("Refresh Logs"):
            st.rerun()

    with tab2:
        st.subheader("🕵️ Advanced Giskard Security Audit")
        
        # FIXED: Corrected the string literals here
        audit_mode = st.selectbox("Select Audit Target", [
            "Hallucination Only (Fast)", 
            "Prompt Injection & Jailbreaking", 
            "Information Disclosure",
            "Full Security Deep Audit (Slow)"
        ])
        
        mode_map = {
            "Hallucination Only (Fast)": "1",
            "Prompt Injection & Jailbreaking": "2",
            "Information Disclosure": "3",
            "Full Security Deep Audit (Slow)": "4"
        }
        
        if st.button("🚀 Execute Giskard Scan"):
            selected_mode = mode_map[audit_mode]
            with st.spinner(f"Giskard is probing for {audit_mode}..."):
                subprocess.run([
                    "/miniconda3/envs/vllm-env/bin/python3", 
                    "/sovereign-ai/scanner.py", 
                    selected_mode
                ])
            st.success("Audit Complete!")

        # Report Viewer
        REPORT_DIR = "/sovereign-ai/reports"
        if os.path.exists(REPORT_DIR):
            reports = sorted([f for f in os.listdir(REPORT_DIR) if f.endswith(".html")], reverse=True)
            if reports:
                selected_report = st.selectbox("Select Audit Report", reports)
                if selected_report:
                    with open(os.path.join(REPORT_DIR, selected_report), 'r') as f:
                        html_data = f.read()
                    # Height increased for better widescreen viewing
                    st.components.v1.html(html_data, height=1200, scrolling=True)
            else:
                st.warning("No reports found. Run a scan to generate your first audit.")

    # Periodic UI refresh
    time.sleep(10)
    st.rerun()

elif st.session_state.get('authentication_status') is False:
    st.error('Access Denied: Invalid Key')
else:
    st.warning('Please enter your Sovereign Access Key to proceed.')
