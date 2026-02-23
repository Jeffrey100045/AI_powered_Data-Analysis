import requests
import os
import time

BASE_URL = "http://127.0.0.1:8889"

def test_drive_upload():
    print(f"Testing Drive Upload on {BASE_URL}...")
    
    # 1. Create a dummy CSV
    filename = f"test_drive_upload_{int(time.time())}.csv"
    with open(filename, "w") as f:
        f.write("id,name,value\n1,TestA,100\n2,TestB,200\n3,TestC,300")
    
    try:
        # 2. Upload to Drive
        print(f"Uploading {filename} to /drive/upload...")
        with open(filename, "rb") as f:
            r = requests.post(f"{BASE_URL}/drive/upload", files={"file": f})
        
        if r.status_code == 200:
            print("✅ Upload successful!")
            data = r.json()
            drive_file = data.get("drive_file", {})
            print(f"File ID: {drive_file.get('id')}")
            print(f"Web Link: {drive_file.get('web_link')}")
            print(f"Preview: {len(data.get('preview', []))} rows")
        else:
            print(f"❌ Upload failed with status {r.status_code}")
            print(r.text)
            
    except Exception as e:
        print(f"❌ Exception during upload: {e}")
    finally:
        # Cleanup
        if os.path.exists(filename):
            os.remove(filename)

if __name__ == "__main__":
    test_drive_upload()
