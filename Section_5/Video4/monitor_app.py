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
    login_placeholder.empty()
    st.title("🛡️ Sovereign AI Command Center")

    # --- 1. NEW TABBED NAVIGATION ---
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
        st.subheader("Vulnerability Scan Reports")
        REPORT_DIR = "/sovereign-ai/reports"
        
        # Trigger a new scan
        if st.button("🚀 Run Full Security Audit"):
            with st.spinner("Red Teaming the Engine..."):
                subprocess.run(["/miniconda3/envs/vllm-env/bin/python3", "/sovereign-ai/scanner.py"])
            st.success("Audit Complete! See reports below.")

        # List and View Reports
        reports = sorted([f for f in os.listdir(REPORT_DIR) if f.endswith(".html")], reverse=True)
        if reports:
            selected_report = st.selectbox("Select a Report to View", reports)
            if selected_report:
                with open(os.path.join(REPORT_DIR, selected_report), 'r') as f:
                    html_data = f.read()
                st.components.v1.html(html_data, height=600, scrolling=True)
        else:
            st.warning("No security reports found. Run an audit to generate one.")

    time.sleep(10)
    st.rerun()
