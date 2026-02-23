import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np
from analyzer import DataAnalyst

def test_gemini():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    print(f"API Key found: {'Yes' if api_key and 'your_api_key' not in api_key else 'No (using template/placeholder)'}")
    
    analyst = DataAnalyst()
    
    # Create dummy data
    data = [
        {"Month": "Jan", "Revenue": 100},
        {"Month": "Feb", "Revenue": 150},
        {"Month": "Mar", "Revenue": 120},
        {"Month": "Apr", "Revenue": 300}, # Spike
        {"Month": "May", "Revenue": 200},
    ]
    
    print("\nTesting AI Analysis Logic...")
    insight = analyst.analyze_chart_with_ai("Line", "Month", "Revenue", data)
    
    if insight:
        print(f"✅ AI Insight: {insight}")
    else:
        print("❌ AI Insight failed or model not initialized. (This is expected if API key is invalid/missing)")

    # Test auto charts with dummy data
    print("\nTesting Auto Charts with dummy CSV...")
    df = pd.DataFrame(data)
    df.to_csv("test_dummy.csv", index=False)
    analyst.load_data("test_dummy.csv")
    
    charts = analyst.get_auto_charts()
    for i, chart in enumerate(charts):
        print(f"\nChart {i+1}: {chart['type']}")
        print(f"Description: {chart['reason']}")

    # Cleanup
    if os.path.exists("test_dummy.csv"):
        os.remove("test_dummy.csv")

if __name__ == "__main__":
    test_gemini()
