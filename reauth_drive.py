import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import base64

# Scopes required
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def main():
    creds = None
    token_path = os.path.join('backend', 'tokens', 'token.pickle')
    creds_path = os.path.join('backend', 'credentials.json')
    
    if not os.path.exists(creds_path):
        print(f"Error: {creds_path} not found. Please ensure your Google Cloud credentials.json is in the backend folder.")
        return

    print("Starting re-authentication...")
    flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
    creds = flow.run_local_server(port=0)
    
    # Save the credentials
    os.makedirs(os.path.dirname(token_path), exist_ok=True)
    with open(token_path, 'wb') as token:
        pickle.dump(creds, token)
    
    print("\n✅ New token.pickle generated successfully!")
    
    # Generate the Base64 string for the user
    with open(token_path, 'rb') as f:
        b64_str = base64.b64encode(f.read()).decode()
    
    print("\n--- COPY THE CODE BELOW ---")
    print(b64_str)
    print("--- END OF CODE ---")
    print("\nPaste the code above into your Render environment variable: GOOGLE_TOKEN_PICKLE_BASE64")

if __name__ == '__main__':
    main()
