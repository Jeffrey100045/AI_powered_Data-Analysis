import requests
import time

def test_ml():
    url_upload = "http://127.0.0.1:8000/upload"
    url_ml = "http://127.0.0.1:8000/ml"
    
    # 1. Upload a numeric dataset
    file_path = "uploads/dirty_test.csv"
    with open(file_path, "rb") as f:
        files = {"file": ("test.csv", f)}
        requests.post(url_upload, files=files)
    
    print("Testing ML on Price...")
    raw_res = requests.get(url_ml, params={"target": "Price"}).json()
    res = raw_res.get("result", {})
    
    if "error" in res:
        print(f"Server Error: {res['error']}")
    else:
        print("--- ML Success ---")
        print(f"Task: {res.get('task')}")
        print(f"Target: {res.get('target')}")
        print(f"Winner: {res.get('winner', {}).get('model')} ({res.get('metric')}: {res.get('winner', {}).get('score')})")
        print(f"Clusters: {res.get('unsupervised')}")
        print(f"Performance Table: {res.get('comparison')}")



    # 3. Try another column (maybe classification if it behaves like one)
    # Price in dirty_test might be seen as regression. 
    # Let's try something else if available.

if __name__ == "__main__":
    time.sleep(2) # Wait for server
    test_ml()
