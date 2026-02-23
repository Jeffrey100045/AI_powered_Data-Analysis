import sys
import os
sys.path.append(os.getcwd())

import pandas as pd
import numpy as np
from backend.processing import DataAnalyst

# Create dummy csv with string numbers
print("Creating test CSV...")
df = pd.DataFrame({
    'Simple': ['1', '2', '3', '4', '5'],
    'Currency': ['$100', '$200', '$300', '$400', '$500'],
    'Comma': ['1,000', '2,000', '3,000', '4,000', '5,000'],
    'Mixed': ['10', '20', 'NA', '40', '50'],
    'Text': ['cat', 'dog', 'bird', 'fish', 'cow']
})
df.to_csv('test_cleaning.csv', index=False)

print("Initializing DataAnalyst...")
analyst = DataAnalyst()

print("Loading data...")
try:
    analyst.load_data('test_cleaning.csv')
    print(f"\nIdentified Numeric Columns: {analyst.num_cols}")
    print(f"\nFinal Data Types:\n{analyst.df.dtypes}")
    
    expected = ['Simple', 'Currency', 'Comma', 'Mixed']
    missing = [c for c in expected if c not in analyst.num_cols]
    
    if not missing:
        print("\n✅ SUCCESS: All numeric-like columns were converted!")
    else:
        print(f"\n❌ FAILURE: Missing columns: {missing}")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
