import pandas as pd
import numpy as np
import io
import traceback

class DataAnalyst:
    def __init__(self):
        self.df = None
        self.num_cols = []

    def load_data(self, file_path):
        try:
            self.df = pd.read_csv(file_path, low_memory=False)
            print(f"Initial dtypes:\n{self.df.dtypes}")
            
            # Simple data cleaning
            self.clean_data()
            
            self.num_cols = self.df.select_dtypes(include=np.number).columns.tolist()
            print(f"Data loaded: {len(self.df)} rows, {len(self.df.columns)} columns.")
            return True
        except Exception as e:
            print(f"Load Error: {str(e)}")
            traceback.print_exc()
            raise e

    def clean_data(self):
        """Standardizes data types and handles missing values."""
        if self.df is None: return

        for col in self.df.columns:
            # Attempt to convert object columns to numeric
            if not pd.api.types.is_numeric_dtype(self.df[col]):
                try:
                    # Check if first few non-null items look like numbers after cleaning
                    sample = self.df[col].dropna().head(10).astype(str)
                    # Keep only digits, dots, and minus signs
                    cleaned_sample = sample.str.replace(r'[^0-9.\-]', '', regex=True)
                    
                    if not cleaned_sample.empty and cleaned_sample.str.len().gt(0).any():
                        # Validate that it can be numeric
                        pd.to_numeric(cleaned_sample, errors='raise')
                        # Apply to full column
                        self.df[col] = pd.to_numeric(self.df[col].astype(str).str.replace(r'[^0-9.\-]', '', regex=True), errors='coerce')
                        print(f"DEBUG: Converted {col} to numeric")
                except Exception as e:
                    # print(f"DEBUG: Could not convert {col} to numeric")
                    pass

            if pd.api.types.is_numeric_dtype(self.df[col]):
                median_val = self.df[col].median()
                self.df[col] = self.df[col].fillna(median_val)
            else:
                self.df[col] = self.df[col].fillna('Unknown')

# Create dummy csv with string numbers
print("Creating test CSV...")
df = pd.DataFrame({
    'Simple': ['1', '2', '3', '4', '5'],
    'Currency': ['$100', '$200', '$300', '$400', '$500'],
    'Comma': ['1,000', '2,000', '3,000', '4,000', '5,000'],
    'Mixed': ['10', '20', 'NA', '40', '50'],
    'Text': ['cat', 'dog', 'bird', 'fish', 'cow']
})
df.to_csv('test_standalone_debug.csv', index=False)

print("Initializing...")
analyst = DataAnalyst()

print("Loading data...")
analyst.load_data('test_standalone_debug.csv')

print(f"\nIdentified Numeric Columns: {analyst.num_cols}")
print(f"\nFinal Data Types:\n{analyst.df.dtypes}")
