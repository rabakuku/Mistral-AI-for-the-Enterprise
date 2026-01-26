To make your **Sovereign AI Engine** truly enterprise-grade, we need it to run as a **background service**. This ensures that even if you close your terminal or your VM restarts, the Streamlit dashboard will be live and accessible at all times. 🛡️




### ⚙️ Video: Automating the UI with Systemd

**Goal:** Create a "Set it and Forget it" service that manages your Streamlit application.

### **Step 1: Create the Service Blueprint** 📝

We will create a service file called `sovereign-ui.service`. This file tells Linux exactly how to launch your web interface using the dedicated Conda environment we built.

Run this command to create the file:

```javascript
# Define the paths
CONDA_PYTHON="/miniconda3/envs/vllm-env/bin/python3"
UI_SERVICE_FILE="/etc/systemd/system/sovereign-ui.service"

# Create the service file
sudo bash -c "cat <<EOF > $UI_SERVICE_FILE
[Unit]
Description=Sovereign AI Streamlit Interface
After=network.target vllm.service

[Service]
# We run from the project root so the app can find /data and /chroma_db
WorkingDirectory=/sovereign-ai

# ExecStart launches Streamlit through our specific Conda Python path
# We use port 8501, which is the default for Streamlit
ExecStart=$CONDA_PYTHON -m streamlit run app.py --server.port 8501 --server.address 0.0.0.0

# If the app crashes, Linux will wait 5 seconds and try to bring it back to life
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF"

```




### **Step 2: Activate the Service** 🚀

Now, let's tell the operating system to load our new configuration and start the UI immediately.

Bash

```javascript
# 1. Reload the system manager to 'see' the new file
sudo systemctl daemon-reload

# 2. Enable the service so it starts on every boot
sudo systemctl enable sovereign-ui

# 3. Start the interface right now
sudo systemctl start sovereign-ui

# 4. Check the status to ensure it's 'active (running)'
systemctl status sovereign-ui

```




### **Step 3: Accessing Your Sovereign Dashboard** 🌐

Your UI is now live! To access it, open your web browser and navigate to your VM's public IP address on port **8501**.

`http://<YOUR_VM_IP>:8501`




### 🧩 **Why this is "Pro" for your Udemy Students** 🎓

| **Feature** | **The Sovereign Benefit** |
| **Dependency Linking** | The `After=vllm.service` line ensures the UI only starts *after* the AI Engine is ready. 🔗 |
| **Auto-Recovery** | If a student uploads a massive, corrupted PDF that crashes the app, the service restarts it automatically. 🔄 |
| **Port Mapping** | By binding to `0.0.0.0`, we ensure the app is reachable from the outside world via our GCP firewall. 🌍 |



