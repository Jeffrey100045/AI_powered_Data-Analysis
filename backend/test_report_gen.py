import os
import pandas as pd
import numpy as np
try:
    from . import reporting
    from . import main
except ImportError:
    import reporting
    import main

# Mock analyst
analyst = main.DataAnalyst()
file_path = "uploads/ecommerce_product_dataset (1).csv"
if os.path.exists(file_path):
    print(f"Loading {file_path}")
    analyst.load_data(file_path)
    analyst.run_ml(analyst.num_cols[0])
    
    # Test report generation
    path = "uploads/test_report.pdf"
    stats = analyst.get_stats()
    ml_results = analyst.ml_results
    print(f"DEBUG: ML Results keys: {list(ml_results.keys()) if ml_results else 'None'}")
    ml_text = ml_results.get("description", "No ML analysis performed.")

    charts = analyst.get_auto_charts()
    
    print("Generating report...")
    reporting.create_pdf_report(path, stats, ml_text, charts, ml_results)
    print(f"Report generated at {path}")
else:
    print(f"File {file_path} not found.")
