import pandas as pd
import numpy as np
import io

class DataAnalyst:
    def __init__(self):
        self.df = None
        self.num_cols = []

    def load_data(self, file_path):
        try:
            self.df = pd.read_csv(file_path, low_memory=False)
            
            # Simple data cleaning
            self.clean_data()
            
            self.num_cols = self.df.select_dtypes(include=np.number).columns.tolist()
            print(f"Data loaded: {len(self.df)} rows, {len(self.df.columns)} columns.")
            return True
        except Exception as e:
            print(f"Load Error: {str(e)}")
            raise e

    def clean_data(self):
        """Standardizes data types and handles missing values."""
        if self.df is None: return

        for col in self.df.columns:
            # Attempt to convert object columns to numeric
            if self.df[col].dtype == 'object':
                try:
                    # Remove common currency/formatting chars
                    cleaned = self.df[col].astype(str).str.replace(r'[$,]', '', regex=True)
                    converted = pd.to_numeric(cleaned, errors='coerce')
                     # If successful (and not all NaNs), replace column
                    if converted.notna().sum() > 0:
                         self.df[col] = converted
                except Exception:
                    pass

            if np.issubdtype(self.df[col].dtype, np.number):
                self.df[col] = self.df[col].fillna(self.df[col].median())
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
df.to_csv('test_standalone.csv', index=False)

print("Initializing...")
analyst = DataAnalyst()

print("Loading data...")
analyst.load_data('test_standalone.csv')

print(f"\nIdentified Numeric Columns: {analyst.num_cols}")
print(f"\nFinal Data Types:\n{analyst.df.dtypes}")

expected = ['Simple', 'Currency', 'Comma', 'Mixed']
found = analyst.num_cols
missing = [c for c in expected if c not in found]

if not missing:
    print("\n✅ SUCCESS: All numeric-like columns were converted!")
else:
    print(f"\n❌ FAILURE: Missing columns: {missing}")
