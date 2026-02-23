from main import DataAnalyst
import os

analyst = DataAnalyst()
file_path = "uploads/ecommerce_product_dataset (1).csv"
if os.path.exists(file_path):
    analyst.load_data(file_path)
    res = analyst.run_ml(analyst.num_cols[0])
    print(f"ML Results Keys: {list(res.keys())}")
    print(f"Decision Adviser: {res.get('decision_adviser')}")
else:
    print("File not found.")
