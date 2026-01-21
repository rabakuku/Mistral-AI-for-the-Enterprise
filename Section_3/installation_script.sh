#! /bin/bash

    #if file is there, do not run starte up script again
    FLAG_FILE="/etc/startup_was_launched"

    if [[ -f "$FLAG_FILE" ]]; then
    echo "Startup script already ran once. Exiting."
    exit 0
    fi    



echo "✅ Installation of ollama!" 
curl -fsSL https://ollama.com/install.sh | sh
# What it does: Downloads and executes the official Ollama installation script, 
# which sets up the background service and CLI.
sudo systemctl enable ollama.service
sudo systemctl start ollama.service
ollama run mistral
echo "✅ Installation of ollama is Complete!" 


echo "✅ Installation of Conda"    
# 1. Connect to your Sovereign AI Engine
# 2. Download and install Miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda3

# 3. Initialize Conda for your shell
source $HOME/miniconda3/bin/activate
conda init bash
source ~/.bashrc
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
conda create -n vllm-env python=3.10 -y
conda activate vllm-env

echo "✅ Installation of Conda is Complete!"



echo "✅ Installation of vllm.service"    
CONDA_PATH="$HOME/miniconda3/envs/vllm-env/bin/python3"
SERVICE_FILE="/etc/systemd/system/vllm.service"

echo "🛡️  Sovereign AI Service Architect"
echo "[*] Creating systemd service the vllm.service "

# 2. Write the service file using sudo
sudo bash -c "cat <<EOF > $SERVICE_FILE
[Unit]
Description=vLLM Sovereign AI Engine
After=network.target nvidia-persistenced.service

[Service]
WorkingDirectory=$HOME
ExecStart=$CONDA_PATH -m vllm.entrypoints.openai.api_server \\
    --model mistralai/Mistral-7B-Instruct-v0.3 \\
    --gpu-memory-utilization 0.9 \\
    --max-model-len 4096 \\
    --port 8000
Restart=always
RestartSec=10
Environment=\"CUDA_VISIBLE_DEVICES=0\"

[Install]
WantedBy=multi-user.target
EOF"

# 3. Finalize and Start
echo "[*] Reloading systemd and starting service..."
sudo systemctl daemon-reload
sudo systemctl enable vllm
sudo systemctl start vllm

echo "------------------------------------------------"
echo "✅ SUCCESS: vLLM is now running as a background service."
echo "View logs:  journalctl -u vllm -f"
echo "Status:     systemctl status vllm"
echo "------------------------------------------------"
echo "✅ Installation of vllm.service is Complete!"   

