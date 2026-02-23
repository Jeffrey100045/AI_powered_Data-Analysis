import os
import pandas as pd
import numpy as np
import re
import sys

# Redirect stdout to a file to avoid terminal garbling
sys.stdout = open('debug_log_clean.txt', 'w', encoding='utf-8')

class DataAnalyst:
    def __init__(self):
        self.df = None

    def load_data(self, file_path):
        print(f"Loading {file_path}...")
        try:
            if file_path.endswith(".csv"):
                self.df = pd.read_csv(file_path, low_memory=False)
            else:
                self.df = pd.read_excel(file_path)
            
            print("Initial Types:")
            print(self.df.dtypes)
            
            self.clean_data()
            
            print("\nFinal Types:")
            print(self.df.dtypes)
            
        except Exception as e:
            print(f"Load Error: {str(e)}")
            raise e

    def clean_data(self):
        if self.df is None: return

        print("\nCleaning Data...")
        for col in self.df.columns:
            print(f"Col: {col}, Dtype: {self.df[col].dtype}")
            # Check if not numeric
            if not pd.api.types.is_numeric_dtype(self.df[col]):
                print(f"Attempting to convert column: {col}")
                try:
                    # Show some raw values
                    print(f"  Sample raw values: {self.df[col].head(5).tolist()}")
                    
                    cleaned = self.df[col].astype(str).str.strip().str.replace(r'[$,]', '', regex=True)
                    cleaned = cleaned.replace('', np.nan)
                    converted = pd.to_numeric(cleaned, errors='coerce')
                    
                    notna_count = converted.notna().sum()
                    total_count = len(converted)
                    print(f"  - Converted {notna_count}/{total_count} values.")
                    
                    # Inspect failures
                    if notna_count < total_count:
                        failures = self.df[col][converted.isna()].head(5).tolist()
                        print(f"  - Sample failures: {failures}")

                    if notna_count > 0:
                         self.df[col] = converted
                         print(f"  - SUCCESS: Converted {col} to numeric.")
                    else:
                         print(f"  - FAILED: {col} remains object.")
                except Exception as e:
                    print(f"  - ERROR converting {col}: {e}")
                    pass

def debug():
    if not os.path.exists("uploads"):
        print("Uploads directory not found.")
        return
        
    files = [f for f in os.listdir("uploads") if f.endswith((".csv", ".xlsx", ".xls"))]
    if not files:
        print("No files found.")
        return
    
    # Get the newest file
    latest_file = max([os.path.join("uploads", f) for f in files], key=os.path.getmtime)
    print(f"Latest file: {latest_file}")
    
    analyst = DataAnalyst()
    analyst.load_data(latest_file)

if __name__ == "__main__":
    debug()
