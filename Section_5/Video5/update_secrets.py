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
