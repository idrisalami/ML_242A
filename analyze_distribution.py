import pandas as pd
import json

def analyze_dataset(csv_path="founders_dataset.csv"):
    df = pd.read_csv(csv_path)
    
    print(f"Total rows: {len(df)}")
    print("-" * 50)
    
    # Categorical columns to analyze
    categorical_cols = [
        'preferred_role', 
        'industry', 
        'is_technical', 
        'education_level',
        'gender'
    ]
    
    for col in categorical_cols:
        if col in df.columns:
            print(f"\nDistribution for '{col}':")
            print(df[col].value_counts(normalize=True).round(3))
            print(f"Raw counts:\n{df[col].value_counts()}")
            print("-" * 30)
            
    # Parse and analyze list columns
    list_cols = ['roles']
    for col in list_cols:
        if col in df.columns:
            # Parse JSON strings if necessary
            parsed_series = df[col].apply(lambda x: json.loads(x) if isinstance(x, str) else x)
            # Flatten list
            all_items = [item for sublist in parsed_series for item in sublist]
            print(f"\nDistribution for items in '{col}':")
            print(pd.Series(all_items).value_counts(normalize=True).round(3))
            print(f"Raw counts:\n{pd.Series(all_items).value_counts()}")
            print("-" * 30)

if __name__ == "__main__":
    analyze_dataset()

