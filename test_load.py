import pandas as pd
import numpy as np
import os
from datetime import datetime

def test_load_data():
    print("=== CSV Data Loading Test ===")
    file_path = 'data/bdm_data.csv'
    print(f"File path: {file_path}")
    print(f"Absolute path: {os.path.abspath(file_path)}")
    print(f"File exists: {os.path.exists(file_path)}")
    print(f"File size: {os.path.getsize(file_path) if os.path.exists(file_path) else 'N/A'} bytes")
    
    try:
        # Load the CSV
        df = pd.read_csv(file_path)
        print(f"\nDataFrame shape: {df.shape}")
        print(f"DataFrame columns: {df.columns.tolist()}")
        
        # Check first few rows
        print("\nFirst 3 rows:")
        print(df.head(3).to_string())
        
        # Check null values
        null_counts = df.isnull().sum()
        print("\nNull value counts:")
        for col, count in null_counts.items():
            print(f"  {col}: {count}")
        
        # Check BDM Names
        print("\nBDM Names:")
        if 'BDM Name' in df.columns:
            bdm_names = df['BDM Name'].dropna().unique()
            print(f"  Unique count: {len(bdm_names)}")
            print(f"  Sample values: {bdm_names[:5].tolist()}")
        else:
            print("  'BDM Name' column not found")
        
        # Check timestamp parsing
        print("\nTimestamp parsing:")
        if 'Timestamp' in df.columns:
            # Create copy of timestamp for testing
            df['Original_Timestamp'] = df['Timestamp'].copy()
            
            # Try automatic parsing
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
            valid_count = df['Timestamp'].notna().sum()
            print(f"  Auto parsing: {valid_count} valid dates of {len(df)}")
            
            # If timestamps were parsed successfully
            if valid_count > 0:
                min_date = df['Timestamp'].min()
                max_date = df['Timestamp'].max()
                print(f"  Date range: {min_date} to {max_date}")
                
                # Create date-related columns
                df['Month'] = df['Timestamp'].dt.month_name()
                df['Week'] = df['Timestamp'].dt.isocalendar().week
                df['Year'] = df['Timestamp'].dt.year
                
                # Check month and year distribution
                print("\nMonth distribution:")
                month_counts = df['Month'].value_counts()
                for month, count in month_counts.items():
                    print(f"  {month}: {count}")
                
                print("\nYear distribution:")
                year_counts = df['Year'].value_counts()
                for year, count in year_counts.items():
                    print(f"  {year}: {count}")
            else:
                print("  No valid dates parsed")
        else:
            print("  'Timestamp' column not found")
        
        # Check numeric columns
        print("\nNumeric columns:")
        for col in ['Keys Sold', 'Key Amount']:
            if col in df.columns:
                # Convert to numeric
                df[col] = pd.to_numeric(df[col], errors='coerce')
                non_null = df[col].notna().sum()
                total = df[col].sum()
                print(f"  {col}: {non_null} non-null values, total sum: {total}")
            else:
                print(f"  '{col}' column not found")
        
        # Try to create performance metrics
        print("\nCreating sample performance data:")
        df_valid = df.dropna(subset=['Timestamp'])
        if not df_valid.empty:
            try:
                performance = df_valid.groupby('BDM Name').agg(
                    visits=('Timestamp', 'count'),
                    keys_sold=('Keys Sold', 'sum')
                ).reset_index()
                
                print(f"  Generated data for {len(performance)} BDMs")
                print(performance.head().to_string())
            except Exception as e:
                print(f"  Error creating performance data: {str(e)}")
        else:
            print("  No valid data for performance metrics")
        
    except Exception as e:
        print(f"\nError loading or processing CSV: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_load_data() 