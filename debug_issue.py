import pandas as pd
import numpy as np
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from processing import DataAnalyst

def test_workflow():
    print("--- Starting Debug Workflow ---")
    
    # 1. Create a dummy CSV
    csv_path = "debug_dataset.csv"
    df = pd.DataFrame({
        'id': range(1, 21),
        'value': np.random.randn(20) * 100,
        'category': ['A', 'B'] * 10,
        'missing_col': [np.nan] * 5 + [1, 2, 3] * 5
    })
    df.to_csv(csv_path, index=False)
    print(f"Created {csv_path}")

    # 2. Initialize Analyst
    analyst = DataAnalyst()
    
    # 3. Test Load Data
    print("\n[Step 1] Loading Data...")
    try:
        preview = analyst.load_data(csv_path)
        print("[OK] Load Data Success")
        print(f"Num Cols: {analyst.num_cols}")
        print(f"All Cols: {getattr(analyst, 'all_cols', 'MISSING')}")
    except Exception as e:
        print(f"[FAIL] Load Data Failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # 4. Test Auto Charts
    print("\n[Step 2] Generating Auto Charts...")
    try:
        charts = analyst.get_auto_charts()
        print(f"[OK] Auto Charts Success. Generated {len(charts)} charts.")
    except Exception as e:
        print(f"[FAIL] Auto Charts Failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # 5. Test ML
    print("\n[Step 3] Running ML...")
    target = 'value'
    try:
        result = analyst.run_ml(target)
        if isinstance(result, dict) and "error" in result:
             print(f"[FAIL] ML Returned Error: {result['error']}")
        else:
             print("[OK] ML Success")
    except Exception as e:
        print(f"[FAIL] ML Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    with open("debug_log.txt", "w", encoding="utf-8") as f:
        sys.stdout = f
        sys.stderr = f
        test_workflow()
