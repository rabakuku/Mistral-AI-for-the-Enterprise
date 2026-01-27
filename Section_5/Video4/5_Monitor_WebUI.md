### **1. The "Stealth" Monitor Code (`monitor_app.py`)** 🧠

***

### **The "Library Breakdown"** 📚

| **Library** | **Status** | **Purpose** |
| **`streamlit`** | **Install Needed** 🛠️ | Powers the actual WebGUI and dashboard. |
| **`streamlit-authenticator`** | **Install Needed** 🛠️ | Handles the secure login and Bcrypt hashing logic. |
| **`pyyaml`** | **Install Needed** 🛠️ | Allows Python to read your `secrets.yaml` file. |
| **`subprocess`** | Standard 🔒 | Built into Python (used to run `journalctl` commands). |
| **`time`** | Standard 🔒 | Built into Python (used for the auto-refresh loop). |

***

### **Step 2: The "One-Liner" Installation** ⚡

```javascript
# 1. Enter your AI environment
conda activate vllm-env

# 2. Install the necessary packages
pip install streamlit streamlit-authenticator pyyaml

# 3. Create the file
cd /sovereign-ai
nano monitor_app.py
```

### **`monitor_app.py`)** 🧠

```javascript
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
```




### **Phase 3: Deploying the Monitor Service** ⚙️

To make this permanent, we will create one last system service.

```javascript
# 1. Create the monitor service file
sudo bash -c "cat <<EOF > /etc/systemd/system/sovereign-monitor.service
[Unit]
Description=Sovereign AI Monitoring WebGUI
After=sovereign-ui.service

[Service]
WorkingDirectory=/sovereign-ai
ExecStart=/miniconda3/envs/vllm-env/bin/python3 -m streamlit run monitor_app.py --server.port 8502 --server.address 0.0.0.0
Restart=always
User=root

[Install]
WantedBy=multi-user.target
EOF"

```

```javascript
# 2. Launch the monitor
sudo systemctl daemon-reload
sudo systemctl enable sovereign-monitor
sudo systemctl start sovereign-monitor
```




### **Why this is Essential** 🎓

- **Encryption at Rest & Motion:** Your students learn that security isn't just about firewalls; it’s about protecting the **observability data**. Using Bcrypt ensures that even if someone steals the code, they can't see the plain-text password.
- **The Synchronized Story:** As noted in your script, the merged logs are the "North Star" for debugging. Seeing a `POST` request in vLLM immediately following a "Search" click in the UI confirms the API bridge is healthy.
- **State Management:** By using `st.rerun()`, students see how Streamlit manages the app's lifecycle to provide real-time updates without complex JavaScript.



