


### **1. The Strategy: Secrets Isolation** 🛡️

We are going to move your login data into a file called `secrets.yaml`. We will then use Linux **File Permissions** to ensure only the `root` user (who runs the service) can read it.

***

### **The "Administrative" Library Breakdown** 📚

| **Library** | **Status** | **Purpose** |
| **`pyyaml`** | **Install Needed** 🛠️ | Allows Python to read and **write** (save) your `secrets.yaml` file. |
| **`streamlit-authenticator`** | **Install Needed** 🛠️ | Provides the `Hasher` utility to turn your plain-text password into a Bcrypt string. |
| **`getpass`** | Standard 🔒 | Built into Python; it hides your password characters as you type them in the terminal. |
| **`os`** | Standard 🔒 | Built into Python; used to lock down file permissions (chmod 600) for security. |

***

### **Step 1: The "Secret Manager" Installation** ⚡

Run this command to make sure your environment can handle the secret-updating logic. This ensures that when you run `update_secrets.py`, it doesn't crash with a `ModuleNotFoundError`.

```javascript
# 1. Enter your AI environment
conda activate vllm-env

# 2. Install the necessary packages
pip install pyyaml streamlit-authenticator

```




### **2. Create the Encrypted/Hidden Secret File** 📄

Run this command to create a secure configuration file. This file will store your username and the hash we generated earlier.

```javascript
# 1. Create the secrets file
cd /sovereign-ai
sudo nano secrets.yaml

```

**Paste the following into the file:**

```javascript
credentials:
  usernames:
    admin_user: # This is the 'hidden' username
      name: "Sovereignty Admin"
      password: "$2b$12$eImiTXuWVxjM72f.7umbRej6.mJ1nN6R4Fv.0W.XjJ6Y1j6y6P.yG"

```

**Crucial Step: Lockdown Permissions** 🔒

This command makes the file "invisible" to any other user or process on the system except for the administrator.

```javascript
sudo chmod 600 /sovereign-ai/secrets.yaml

```







### **1. The "Secret Manager" Script (`update_secrets.py`)** 🛠️

This script will prompt you for a username and password, hash the password using the standard `streamlit-authenticator` logic, and then update your `secrets.yaml` file automatically.

```javascript
import yaml
import getpass
import streamlit_authenticator as stauth
from yaml.loader import SafeLoader
import os

def update_sovereign_secrets():
    print("------------------------------------------------")
    print("🛡️  Sovereign AI: Secret Manager (v2026)")
    print("------------------------------------------------")

    # 1. Secure Inputs
    # getpass ensures the password doesn't show up on screen
    new_username = input("[+] Enter new Admin Username: ")
    new_password = getpass.getpass("[+] Enter new Admin Password: ")
    confirm_password = getpass.getpass("[+] Confirm Admin Password: ")

    if new_password != confirm_password:
        print("[-] ❌ Error: Passwords do not match. Exiting.")
        return

    # 2. Generate the Secure Bcrypt Hash
    # FIX: We now use the static .hash() method directly.
    try:
        hashed_password = stauth.Hasher.hash(new_password)
    except Exception as e:
        print(f"[-] ❌ Hashing failed: {e}")
        return

    # 3. Prepare the Data Structure
    # This structure is designed to be read by monitor_app.py
    secret_data = {
        'credentials': {
            'usernames': {
                new_username: {
                    'name': "Sovereignty Admin",
                    'password': hashed_password
                }
            }
        }
    }

    # 4. Write to secrets.yaml
    file_path = 'secrets.yaml'
    try:
        with open(file_path, 'w') as file:
            yaml.dump(secret_data, file, default_flow_style=False)
        
        # 5. Lockdown File Permissions
        # chmod 600 ensures only the owner can read/write this secret file
        os.chmod(file_path, 0o600)
        
        print("------------------------------------------------")
        print(f"✅ Success! Secrets updated for: '{new_username}'")
        print(f"🔒 Permissions locked to 600 (Root/Owner Only).")
        print("------------------------------------------------")
    
    except Exception as e:
        print(f"[-] ❌ Error updating secrets: {e}")

if __name__ == "__main__":
    update_sovereign_secrets()
```




### **2. How to Deploy & Use It** 🚀

To make this easy for your Udemy students, follow these steps in order:

```javascript
# 1. Move to your project directory
cd /sovereign-ai

# 2. Create the file
nano update_secrets.py

# 3. Paste the code above, save and exit (Ctrl+O, Enter, Ctrl+X)

# 4. Run the script
# IMPORTANT: Ensure your vllm-env is active so libraries are found
conda activate vllm-env
python3 update_secrets.py

```




### **Pro-Tip: The Security Layer** 🎓

| **Library / Command** | **Why it's "Pro"** |
| **`getpass`** | **Anti-Snoop:** It prevents the password from being echoed back to the screen, which is essential if someone is watching over your shoulder. 🕵️ |
| **`os.chmod(file, 0o600)`** | **Hardened Access:** Even if a hacker gains access to a lower-level user account on your VM, they cannot open this file. It is locked to the owner only. 🛡️ |
| **`yaml.dump`** | **Clean Config:** It ensures the file is perfectly formatted, preventing any "Syntax Errors" that would break your WebGUI. 📂 |




