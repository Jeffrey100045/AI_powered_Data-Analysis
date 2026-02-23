import os
import sys
from google_auth_oauthlib.flow import InstalledAppFlow

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

SCOPES = ['https://www.googleapis.com/auth/drive.file']
CREDENTIALS_PATH = 'backend/credentials.json'

def test_auth():
    print("Starting Auth Test...")
    if not os.path.exists(CREDENTIALS_PATH):
        print(f"Error: {CREDENTIALS_PATH} not found")
        return

    try:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
        # We don't want to actually wait for the user, just see if it starts and opens browser
        # but run_local_server is blocking.
        print("Flow created. Attempting to start local server...")
        # Use a timeout or just print that we are about to start
        print("NOTE: This will try to open a browser window.")
        # We'll use a try-except to see if it even starts
        creds = flow.run_local_server(port=0, open_browser=True, timeout_seconds=10)
        print("Success?")
    except Exception as e:
        print(f"Caught expected or unexpected error: {e}")

if __name__ == "__main__":
    test_auth()
