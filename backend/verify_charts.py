import requests
import json

BASE_URL = "http://127.0.0.1:8889"

def check_session():
    print(f"Checking /session_state on {BASE_URL}...")
    try:
        r = requests.get(f"{BASE_URL}/session_state")
        if r.status_code == 200:
            data = r.json()
            if data.get("active"):
                print("✅ Session Active")
                preview = data.get("preview", [])
                if preview:
                    print(f"Preview (first row): {preview[0]}")
                    # Check types of first row values
                    for k, v in preview[0].items():
                        print(f"  {k}: {type(v).__name__} ({v})")
                
                charts = data.get("auto_charts", [])
                print(f"✅ Found {len(charts)} charts.")
                for i, chart in enumerate(charts):
                    print(f"Chart {i+1}: {chart.get('type')}")
            else:
                print("❌ Session Not Active")
        else:
            print(f"❌ Error: {r.status_code}")
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    check_session()
