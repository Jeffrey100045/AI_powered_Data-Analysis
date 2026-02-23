import requests
import os

url = "http://127.0.0.1:8000/upload"
file_path = "uploads/dirty_test.csv"

if not os.path.exists(file_path):
    print(f"Error: {file_path} not found")
else:
    with open(file_path, "rb") as f:
        files = {"file": (os.path.basename(file_path), f, "text/csv")}
        try:
            response = requests.post(url, files=files)
            print(f"Status Code: {response.status_code}")
            print(f"Response Body: {response.json()}")
        except Exception as e:
            print(f"Connection failed: {str(e)}")
