#! /bin/bash

    #if file is there, do not run starte up script again
    FLAG_FILE="/etc/startup_was_launched"

    if [[ -f "$FLAG_FILE" ]]; then
    echo "Startup script already ran once. Exiting."
    exit 0
    fi    

echo "✅ Installation of Conda"    
# 1. Connect to your Sovereign AI Engine
gcloud compute ssh sovereign-ai-engine --zone=us-central1-a

# 2. Download and install Miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda3

conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
# 3. Initialize Conda for your shell
source $HOME/miniconda3/bin/activate
conda init bash
source ~/.bashrc

echo "✅ Installation of Conda is Complete!"
