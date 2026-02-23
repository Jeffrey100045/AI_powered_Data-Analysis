import requests

BASE_URL = "http://127.0.0.1:8888"

def test_api():
    # 1. Create a dummy CSV
    with open("test_api.csv", "w") as f:
        f.write("id,name,value\n1,Alpha,100\n2,Beta,200\n3,Gamma,300")
    
    # 2. Upload
    print("Testing /upload...")
    with open("test_api.csv", "rb") as f:
        r = requests.post(f"{BASE_URL}/upload", files={"file": f})
    print(r.json())
    
    # 3. Test Filter
    print("\nTesting /filter...")
    r = requests.get(f"{BASE_URL}/filter", params={"query": "value > 150"})
    print(r.json())
    
    # 4. Test Auto Charts
    print("\nTesting /auto_charts...")
    r = requests.get(f"{BASE_URL}/auto_charts")
    print(r.json())

if __name__ == "__main__":
    test_api()
