import pandas as pd
import numpy as np
import os
import re

def debug_clean_data(df):
    num_cols = []
    # 1. Attempt to convert object columns to numeric if they look like numbers
    for col in df.columns:
        if pd.api.types.is_object_dtype(df[col]):
            print(f"Checking column: {col}")
            # Skip if mostly empty
            if df[col].isna().all(): 
                print(f"  {col} is all NaN, skipping")
                continue
            
            # Check if first few non-null items look like numbers (stripping common symbols)
            sample = df[col].dropna().head(10).astype(str)
            # More robust regex: remove anything that isn't a digit, dot, or minus sign
            cleaned_sample = sample.str.replace(r'[^0-9.\-]', '', regex=True)
            print(f"  Sample: {sample.tolist()}")
            print(f"  Cleaned: {cleaned_sample.tolist()}")
            
            try:
                if not cleaned_sample.empty:
                    pd.to_numeric(cleaned_sample, errors='raise')
                    df[col] = pd.to_numeric(df[col].astype(str).str.replace(r'[^0-9.\-]', '', regex=True), errors='coerce')
                    print(f"  SUCCESS: Converted {col} to numeric")
            except Exception as e:
                print(f"  FAILED: {str(e)}")
                pass

    # 2. Fill missing values
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(df[col].median() if not df[col].isna().all() else 0)
        else:
            df[col] = df[col].fillna('Unknown')
    
    # 3. Update cached column lists
    new_num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    print(f"Final Numeric columns: {new_num_cols}")
    print("Dtypes:")
    print(df.dtypes)
    print("Head:")
    print(df.head())
    return df


if __name__ == "__main__":
    df = pd.read_csv('uploads/dirty_test.csv', low_memory=False)
    debug_clean_data(df)
