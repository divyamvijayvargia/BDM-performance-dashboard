import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

def load_data():
    try:
        # Use the path from config instead of hardcoding it
        file_path = app.config['DATA_FILE']
        print(f"Attempting to load data from {file_path}")
        df = pd.read_csv(file_path)
        
        # These are the actual columns from your CSV file
        expected_columns = [
            'Timestamp', 'Shop Name', 'RocketPay Registered Number', 'City', 'State', 
            'BDM Name', 'Visit Status', 'Latitude', 'Longitude', 'Keys Sold', 
            'Key Amount', 'Current Key Balance', 'Wallet Transaction ID'
        ]
        
        # Check if all expected columns exist
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            print(f"Warning: Missing columns in CSV: {missing_columns}")
        
        # Convert Timestamp column to datetime with the format from config
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], format=app.config['DATE_FORMAT'], errors='coerce')
        
        # Fill missing values and convert to proper types
        df['Keys Sold'] = df['Keys Sold'].fillna(0).astype(int)
        df['Key Amount'] = df['Key Amount'].fillna(0).astype(float)
        
        # Create new date-related columns
        df['Month'] = df['Timestamp'].dt.month_name()
        df['Week'] = df['Timestamp'].dt.isocalendar().week
        df['Year'] = df['Timestamp'].dt.year
        df['Date'] = df['Timestamp'].dt.date
        
        print(f"Successfully loaded data: {len(df)} rows")
        print(f"First row sample: {df.iloc[0] if len(df) > 0 else 'No data'}")
        return df
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        import traceback
        traceback.print_exc()
        # Return an empty DataFrame with all the required columns
        return pd.DataFrame(columns=['Timestamp', 'BDM Name', 'Shop Name', 'Keys Sold', 
                                    'Key Amount', 'State', 'Month', 'Week', 'Year', 'Date'])

def get_bdm_performance(df, time_filter=None, month=None, year=None, state=None):
    """Calculate BDM performance metrics based on filters"""
    # Apply filters
    filtered_df = df.copy()
    
    # Apply time filter (daily, weekly, monthly)
    current_date = datetime.now().date()
    
    if time_filter == 'daily':
        filtered_df = filtered_df[filtered_df['Date'] == current_date]
    elif time_filter == 'weekly':
        one_week_ago = current_date - timedelta(days=7)
        filtered_df = filtered_df[filtered_df['Date'] >= one_week_ago]
    elif time_filter == 'monthly':
        # If specific month is provided, filter by it
        if month and year:
            filtered_df = filtered_df[(filtered_df['Month'] == month) & (filtered_df['Year'] == int(year))]
        else:
            # Default to current month
            current_month = datetime.now().month
            current_year = datetime.now().year
            filtered_df = filtered_df[(filtered_df['Timestamp'].dt.month == current_month) & (filtered_df['Timestamp'].dt.year == current_year)]
    
    # Apply state filter
    if state and state != 'All':
        filtered_df = filtered_df[filtered_df['State'] == state]
    
    # Calculate performance metrics grouped by BDM
    if not filtered_df.empty:
        performance = filtered_df.groupby('BDM Name').agg(
            visits=('Timestamp', 'count'),
            unique_merchants=('Shop Name', 'nunique'),
            keys_sold=('Keys Sold', 'sum'),
            key_amount=('Key Amount', 'sum')
        ).reset_index()
        
        # Rename columns for clarity
        performance.columns = ['BDM Name', '# Visits', '# Unique Merchants Visited', '# Keys Sold', 'Key Sales Amount']
        
        # Format the sales amount
        performance['Key Sales Amount'] = performance['Key Sales Amount'].apply(lambda x: f"₹{x:,.2f}")
        
        return performance.to_dict('records')
    else:
        return []

@app.route('/')
def dashboard():
    """Render the main dashboard page"""
    df = load_data()
    
    # Print debugging info
    print(f"DataFrame shape: {df.shape}")
    if not df.empty:
        print(f"Data sample: {df.head(2)}")
    else:
        print("Warning: DataFrame is empty!")
    
    # Get unique months and years for the filter
    months = sorted(df['Month'].dropna().astype(str).unique().tolist())
    years = sorted(df['Year'].unique().tolist())
    
    # Get the list of states from the data
    states = sorted(df['State'].unique().tolist())
    states.insert(0, 'All')  # Add 'All' option at the beginning
    
    # Calculate initial performance data (default: monthly, all states)
    performance_data = get_bdm_performance(df, time_filter='monthly')
    print(f"Performance data entries: {len(performance_data)}")
    
    return render_template('dashboard.html', 
                           performance_data=performance_data,
                           months=months,
                           years=years,
                           states=states)

@app.route('/filter-data', methods=['POST'])
def filter_data():
    """API endpoint to filter data based on user selections"""
    df = load_data()
    
    # Get filter parameters from request
    time_filter = request.form.get('time_filter', 'monthly')
    month = request.form.get('month')
    year = request.form.get('year')
    state = request.form.get('state')
    
    # Get filtered performance data
    performance_data = get_bdm_performance(df, time_filter, month, year, state)
    
    return jsonify(performance_data)

if __name__ == '__main__':
    app.run(debug=True)