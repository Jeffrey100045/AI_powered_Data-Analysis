import os
import json
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.file']

class GoogleDriveService:
    def __init__(self, credentials_path=None, token_path=None):
        # Determine paths relative to this script
        base_dir = os.path.dirname(__file__)
        self.credentials_path = credentials_path or os.path.join(base_dir, 'credentials.json')
        self.token_path = token_path or os.path.join(base_dir, 'tokens', 'token.pickle')
        self.creds = None
        self.service = None
        self._file_cache = None
        
        # Create tokens directory if it doesn't exist
        os.makedirs(os.path.dirname(self.token_path), exist_ok=True)
    
    def authenticate(self):
        """Authenticate with Google Drive using OAuth2."""
        import base64
        print("DEBUG: authenticate() called")
        
        # 1. Try to load from GOOGLE_TOKEN_PICKLE_BASE64 (Best for Render)
        env_token_b64 = os.environ.get('GOOGLE_TOKEN_PICKLE_BASE64')
        if env_token_b64:
            print(f"DEBUG: GOOGLE_TOKEN_PICKLE_BASE64 found (length: {len(env_token_b64)})")
            try:
                # Clean the string from potential spaces or newlines
                env_token_b64 = env_token_b64.strip().replace('\n', '').replace('\r', '')
                token_data = base64.b64decode(env_token_b64)
                self.creds = pickle.loads(token_data)
                print(f"DEBUG: Successfully loaded credentials from env var. Valid: {self.creds.valid}")
            except Exception as e:
                print(f"DEBUG: Failed to decode/load token from env var: {e}")

        # 2. Check local token.pickle if env token failed
        if (not self.creds or not self.creds.valid) and os.path.exists(self.token_path):
            print(f"DEBUG: Checking local token.pickle at {self.token_path}")
            try:
                with open(self.token_path, 'rb') as token:
                    self.creds = pickle.load(token)
                print(f"DEBUG: Loaded local token.pickle. Valid: {self.creds.valid}")
            except Exception as e:
                print(f"DEBUG: Failed to load local token.pickle: {e}")
        
        # 3. If there are no (valid) credentials, try to refresh or init
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                print("DEBUG: Attempting to refresh expired credentials...")
                try:
                    self.creds.refresh(Request())
                    print("DEBUG: Token refreshed successfully")
                except Exception as e:
                    print(f"DEBUG: Token refresh failed: {e}")
                    # If refresh fails, we might still be able to use GOOGLE_CREDENTIALS_JSON to re-auth
                    self.creds = None
            
            if not self.creds:
                print("DEBUG: No valid credentials found. Checking GOOGLE_CREDENTIALS_JSON")
                # Check for environment variable credentials
                env_creds = os.environ.get('GOOGLE_CREDENTIALS_JSON')
                if env_creds:
                    print(f"DEBUG: GOOGLE_CREDENTIALS_JSON found (length: {len(env_creds)})")
                    try:
                        creds_dict = json.loads(env_creds)
                        flow = InstalledAppFlow.from_client_config(creds_dict, SCOPES)
                        # run_local_server setup for headless console login if possible
                        self.creds = flow.run_local_server(port=0, open_browser=False)
                        print("DEBUG: Authenticated using GOOGLE_CREDENTIALS_JSON")
                    except Exception as e:
                        print(f"DEBUG: Failed to authenticate with GOOGLE_CREDENTIALS_JSON: {e}")
                
                # Fallback to credentials.json file
                if not self.creds:
                    if not os.path.exists(self.credentials_path):
                        print(f"DEBUG: Credentials file not found at {self.credentials_path}")
                        raise FileNotFoundError(
                            f"Credentials file not found at {self.credentials_path}. "
                            "Please download OAuth2 credentials from Google Cloud Console or set GOOGLE_TOKEN_PICKLE_BASE64 environment variable."
                        )
                    
                    print(f"DEBUG: Found credentials.json at {self.credentials_path}")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, SCOPES)
                    self.creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run if we have a path
            try:
                if self.creds:
                    with open(self.token_path, 'wb') as token:
                        pickle.dump(self.creds, token)
                    print(f"DEBUG: Saved session token to {self.token_path}")
            except Exception as e:
                print(f"DEBUG: Error saving session token: {e}")
        
        if not self.creds:
            print("DEBUG: Authentication failed completely - self.creds is None")
            raise Exception("Authentication failed. No credentials provided.")
            
        self.service = build('drive', 'v3', credentials=self.creds)
        print("DEBUG: Google Drive service built successfully")
        return True
    
    def is_authenticated(self):
        """Check if user is authenticated."""
        if os.path.exists(self.token_path):
            try:
                with open(self.token_path, 'rb') as token:
                    creds = pickle.load(token)
                    return creds and creds.valid
            except:
                return False
        return False
    
    def upload_file(self, file_path, file_name=None, folder_id=None):
        """Upload a file to Google Drive."""
        if not self.service:
            self.authenticate()
        
        if not file_name:
            file_name = os.path.basename(file_path)
        
        file_metadata = {'name': file_name}
        if folder_id:
            file_metadata['parents'] = [folder_id]
        
        # Determine MIME type
        mime_type = 'application/octet-stream'
        if file_path.endswith('.csv'):
            mime_type = 'text/csv'
        elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
            mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        
        media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
        
        try:
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, size, createdTime, webViewLink'
            ).execute()
            
            return {
                'success': True,
                'file_id': file.get('id'),
                'name': file.get('name'),
                'size': file.get('size'),
                'created_time': file.get('createdTime'),
                'web_link': file.get('webViewLink')
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def download_file(self, file_id, destination_path):
        """Download a file from Google Drive."""
        if not self.service:
            self.authenticate()
        
        try:
            request = self.service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            # Write to file
            fh.seek(0)
            with open(destination_path, 'wb') as f:
                f.write(fh.read())
            
            return {
                'success': True,
                'path': destination_path
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def list_files(self, page_size=20, query=None, use_cache=True):
        """List files from Google Drive with basic caching."""
        if use_cache and self._file_cache:
            return self._file_cache

        if not self.service:
            self.authenticate()
        
        try:
            if not query:
                # Direct query for common data formats
                query = "mimeType='text/csv' or mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'"
            
            results = self.service.files().list(
                pageSize=page_size,
                q=query,
                fields="files(id, name, size, modifiedTime)",
                orderBy="modifiedTime desc"
            ).execute()
            
            self._file_cache = {
                'success': True,
                'files': results.get('files', [])
            }
            return self._file_cache
        except Exception as e:
            return {'success': False, 'error': str(e)}

    
    def get_file_info(self, file_id):
        """Get information about a specific file."""
        if not self.service:
            self.authenticate()
        
        try:
            file = self.service.files().get(
                fileId=file_id,
                fields='id, name, size, createdTime, modifiedTime, webViewLink'
            ).execute()
            
            return {
                'success': True,
                'file': file
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_file(self, file_id):
        """Delete a file from Google Drive."""
        if not self.service:
            self.authenticate()
        
        try:
            self.service.files().delete(fileId=file_id).execute()
            return {
                'success': True,
                'message': 'File deleted successfully'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
