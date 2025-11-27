import pandas as pd
import os

def check_for_na(directory):
    print(f"\n--- Checking for N/A values in {directory} ---")
    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            filepath = os.path.join(directory, filename)
            try:
                df = pd.read_csv(filepath)
                
                # Check for literal "N/A" string
                na_string_counts = (df == "N/A").sum()
                if na_string_counts.sum() > 0:
                    print(f"\nFile: {filename}")
                    print("Columns with 'N/A' string:")
                    print(na_string_counts[na_string_counts > 0])
                
                # Check for null/NaN values
                null_counts = df.isnull().sum()
                if null_counts.sum() > 0:
                    print(f"\nFile: {filename}")
                    print("Columns with NULL/NaN values:")
                    print(null_counts[null_counts > 0])
                    
            except Exception as e:
                print(f"Error reading {filename}: {e}")

if __name__ == "__main__":
    # Check processed data directories
    base_dir = "data/processed"
    check_for_na(os.path.join(base_dir, "procurement"))
    check_for_na(os.path.join(base_dir, "marketing"))

