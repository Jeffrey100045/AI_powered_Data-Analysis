try:
    from .main import DataAnalyst
    from . import reporting
except ImportError:
    from main import DataAnalyst
    import reporting
import os

analyst = DataAnalyst()
file_path = "uploads/ecommerce_product_dataset (1).csv"
if os.path.exists(file_path):
    analyst.load_data(file_path)
    # DO NOT RUN ML
    
    path = "uploads/no_ml_test_report.pdf"
    stats = analyst.get_stats()
    ml_results = analyst.ml_results # Should be None
    ml_text = ml_results.get("description", "No ML analysis performed.") if ml_results else "No ML analysis performed."
    charts = analyst.get_auto_charts()
    
    print("Generating report (no ML run)...")
    reporting.create_pdf_report(path, stats, ml_text, charts, ml_results)
    print(f"Report generated at {path}")
else:
    print("File not found.")
