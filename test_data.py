import pandas as pd
import numpy as np
from datetime import datetime
import os

print("Starting CSV analysis...")
file_path = 'data/bdm_data.csv'
print(f"Reading CSV from: {os.path.abspath(file_path)}")
print(f"File exists: {os.path.exists(file_path)}")

try:
    # Read the CSV file
    df = pd.read_csv(file_path)
    print(f"CSV loaded successfully. Shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    
    # Check for null values
    print("\nNull value counts:")
    for col in df.columns:
        null_count = df[col].isna().sum()
        print(f"  {col}: {null_count}")
    
    # Check BDM Names
    bdm_names = df['BDM Name'].dropna().unique().tolist()
    print(f"\nUnique BDM Names ({len(bdm_names)}):")
    print(bdm_names[:10])  # Print first 10
    
    # Convert timestamp to datetime
    print("\nAttempting to convert timestamps...")
    date_formats = ['%d/%m/%Y %H:%M:%S', '%d/%m/%Y %H:%M']
    for date_format in date_formats:
        try:
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], format=date_format, errors='coerce')
            print(f"Conversion successful with format: {date_format}")
            break
        except Exception as e:
            print(f"Failed to parse with format {date_format}: {str(e)}")
    
    # Check timestamp conversion
    valid_timestamps = df['Timestamp'].notna().sum()
    print(f"Valid timestamps: {valid_timestamps} of {len(df)}")
    
    # Check time range
    if valid_timestamps > 0:
        min_date = df['Timestamp'].min()
        max_date = df['Timestamp'].max()
        print(f"Date range: {min_date} to {max_date}")
    
    # Check key sales
    df['Keys Sold'] = df['Keys Sold'].fillna(0).astype(int)
    df['Key Amount'] = df['Key Amount'].fillna(0).astype(float)
    
    total_keys = df['Keys Sold'].sum()
    total_amount = df['Key Amount'].sum()
    print(f"\nTotal Keys Sold: {total_keys}")
    print(f"Total Key Amount: {total_amount}")
    
    # Create sample performance data
    print("\nCreating sample performance data...")
    df_with_timestamp = df.dropna(subset=['Timestamp'])
    if not df_with_timestamp.empty:
        performance = df_with_timestamp.groupby('BDM Name').agg(
            visits=('Timestamp', 'count'),
            unique_merchants=('Shop Name', 'nunique'),
            keys_sold=('Keys Sold', 'sum'),
            key_amount=('Key Amount', 'sum')
        ).reset_index()
        
        print(f"Performance data generated for {len(performance)} BDMs:")
        print(performance.head())
    else:
        print("No valid data available for performance metrics")
    
except Exception as e:
    print(f"Error analyzing CSV: {str(e)}")
    import traceback
    traceback.print_exc() 