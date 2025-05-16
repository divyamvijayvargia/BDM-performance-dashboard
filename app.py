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
        
        # Try to read the CSV file with UTF-8 encoding
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            # If UTF-8 fails, try other encodings
            df = pd.read_csv(file_path, encoding='latin-1')
        
        print(f"CSV file loaded successfully with shape: {df.shape}")
        total_rows = len(df)
        
        # Convert Timestamp to datetime (use automatic format detection with dayfirst=True)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce', dayfirst=True)
        
        # Report on null values
        null_timestamp_count = df['Timestamp'].isna().sum()
        print(f"Null timestamps: {null_timestamp_count} of {len(df)}")
        
        # IMPORTANT: Do NOT drop rows with null timestamps
        # Instead, fill null timestamps with a default date to preserve all data
        if null_timestamp_count > 0:
            print(f"Filling {null_timestamp_count} null timestamps with a default date")
            df['Timestamp'].fillna(pd.Timestamp('2025-01-01'), inplace=True)
        
        # Convert numeric columns properly
        df['Keys Sold'] = pd.to_numeric(df['Keys Sold'], errors='coerce').fillna(0).astype(int)
        df['Key Amount'] = pd.to_numeric(df['Key Amount'], errors='coerce').fillna(0).astype(float)
        
        # Ensure text columns have valid values
        df['BDM Name'] = df['BDM Name'].fillna('Unknown')
        df['Shop Name'] = df['Shop Name'].fillna('Unknown')
        df['State'] = df['State'].fillna('Unknown')
        
        # Create date-related columns
        df['Month'] = df['Timestamp'].dt.month_name()
        df['Week'] = df['Timestamp'].dt.isocalendar().week
        df['Year'] = df['Timestamp'].dt.year
        df['Date'] = df['Timestamp'].dt.date
        
        # Print summary and verify we maintained all rows
        print(f"Data loaded successfully: {len(df)} rows with {df['BDM Name'].nunique()} unique BDMs")
        if len(df) != total_rows:
            print(f"WARNING: Row count changed from {total_rows} to {len(df)}!")
        else:
            print(f"Confirmed all {total_rows} rows were preserved")
        
        return df
        
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        import traceback
        traceback.print_exc()
        return create_dummy_data()

def create_dummy_data():
    """Create dummy data if the real data cannot be loaded"""
    print("Creating dummy data for demonstration purposes")
    # Create a date range for the last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Create dummy data
    data = []
    bdm_names = ['John Doe', 'Jane Smith', 'Robert Johnson', 'Emma Williams']
    states = ['MAHARASHTRA', 'GUJARAT', 'KARNATAKA', 'DELHI']
    
    for date in dates:
        for bdm in bdm_names:
            # Add several entries per day per BDM
            for i in range(np.random.randint(1, 5)):
                data.append({
                    'Timestamp': date + timedelta(hours=np.random.randint(9, 18)),
                    'BDM Name': bdm,
                    'Shop Name': f'Shop {np.random.randint(1, 100)}',
                    'State': np.random.choice(states),
                    'Keys Sold': np.random.randint(0, 10),
                    'Key Amount': np.random.randint(0, 2000),
                })
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Add additional columns
    df['Month'] = df['Timestamp'].dt.month_name()
    df['Week'] = df['Timestamp'].dt.isocalendar().week
    df['Year'] = df['Timestamp'].dt.year
    df['Date'] = df['Timestamp'].dt.date
    
    print(f"Created dummy data with {len(df)} rows")
    return df

def get_bdm_performance(df, time_filter=None, month=None, year=None, state=None, start_date=None, end_date=None):
    """Calculate BDM performance metrics based on filters"""
    try:
        # Apply filters
        filtered_df = df.copy()
        original_count = len(filtered_df)
        print(f"Starting filtering with {original_count} records")
        
        # Check if DataFrame is empty
        if filtered_df.empty:
            print("Warning: Empty DataFrame provided for filtering")
            return []
        
        # Debug info - print dimensions and sample data
        print(f"Original data dimensions: {filtered_df.shape}, unique BDMs: {filtered_df['BDM Name'].nunique()}")
        
        # Check for "Show All" condition
        is_show_all = ((time_filter == 'monthly' and not month and not year) or 
                       (time_filter == 'daily' and not start_date) or 
                       (time_filter == 'weekly' and (not start_date or not end_date))) and state == 'All'
        
        if is_show_all:
            print("Show all data request detected - skipping all time filters")
            # Skip time filters but still apply state filter if needed
        else:
            # Apply time filter (daily, weekly, monthly)
            if time_filter == 'daily':
                if start_date:
                    try:
                        # Parse the start date from MM/DD/YYYY format
                        selected_date = datetime.strptime(start_date, '%m/%d/%Y').date()
                        filtered_df = filtered_df[filtered_df['Date'] == selected_date]
                        print(f"Daily filter applied for selected date {selected_date}: {len(filtered_df)} records remaining")
                    except (ValueError, TypeError) as e:
                        print(f"Error parsing start date: {str(e)}")
                        # Default to showing all data if parsing fails
                        print("Showing all data since date parsing failed")
                else:
                    # If no start date is provided, default to showing all data
                    print("No specific date selected for daily filter, showing all data")
            elif time_filter == 'weekly':
                if start_date and end_date:
                    try:
                        # Parse the date range from MM/DD/YYYY format
                        start = datetime.strptime(start_date, '%m/%d/%Y').date()
                        end = datetime.strptime(end_date, '%m/%d/%Y').date()
                        filtered_df = filtered_df[(filtered_df['Date'] >= start) & (filtered_df['Date'] <= end)]
                        print(f"Weekly filter applied from {start} to {end}: {len(filtered_df)} records remaining")
                    except (ValueError, TypeError) as e:
                        print(f"Error parsing date range: {str(e)}")
                        # Default to showing all data if parsing fails
                        print("Showing all data since date range parsing failed")
                else:
                    # If no date range is provided, default to showing all data
                    print("No specific week selected for weekly filter, showing all data")
            elif time_filter == 'monthly':
                # If specific month is provided, filter by it
                if month and year and month != '' and year != '':
                    try:
                        # Handle both numeric month and month name
                        if month.isdigit():
                            month_num = int(month)
                        else:
                            try:
                                month_num = datetime.strptime(month, '%B').month
                            except ValueError:
                                # Try abbreviated month name
                                month_num = datetime.strptime(month, '%b').month
                        
                        year_num = int(year)
                        print(f"Applying monthly filter for month={month_num}, year={year_num}")
                        
                        # Filter by month number and year
                        filtered_df = filtered_df[(filtered_df['Timestamp'].dt.month == month_num) & 
                                                (filtered_df['Timestamp'].dt.year == year_num)]
                    except (ValueError, TypeError) as e:
                        print(f"Error parsing month/year: {str(e)}")
                        # Show all data instead of defaulting to a specific month/year
                        print("Showing all data since month/year parsing failed")
                else:
                    # Show all data if no month/year specified
                    print("No month/year specified. Showing all data")
        
        # Apply state filter
        if state and state != 'All':
            state_count_before = len(filtered_df)
            filtered_df = filtered_df[filtered_df['State'] == state]
            print(f"State filter applied for '{state}': {state_count_before} → {len(filtered_df)} records")
        
        print(f"After all filtering: {len(filtered_df)} of {original_count} records remaining")
        
        # If we don't have any data after filtering, return empty list
        if filtered_df.empty:
            print("No data matches the current filters")
            return []
        
        # Debug info - print filtered dimensions before aggregation
        print(f"Filtered data before aggregation: {filtered_df.shape}, unique BDMs: {filtered_df['BDM Name'].nunique()}")
        
        # Calculate performance metrics grouped by BDM
        try:
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
            
            result = performance.to_dict('records')
            print(f"Generated performance data for {len(result)} BDMs with a total of {filtered_df.shape[0]} rows")
            return result
        except Exception as e:
            print(f"Error calculating performance metrics: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
            
    except Exception as e:
        print(f"Error in get_bdm_performance: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

@app.route('/')
def dashboard():
    """Render the main dashboard page"""
    try:
        df = load_data()
        
        # Print debugging info
        print(f"DataFrame shape: {df.shape}")
        if not df.empty:
            print(f"Data sample: {df.head(2)}")
        else:
            print("Warning: DataFrame is empty!")
        
        # Get unique months and years for the filter
        # Ensure we have valid entries only
        months = sorted(df['Month'].dropna().astype(str).unique().tolist())
        years = sorted(df['Year'].dropna().unique().tolist())
        
        if not months:
            # If no valid months, add current month as a fallback
            months = [datetime.now().strftime('%B')]
        
        if not years:
            # If no valid years, add current year as a fallback
            years = [datetime.now().year]
        
        # Get the list of states from the data
        states = sorted(df['State'].dropna().unique().tolist())
        
        # Add 'All' option at the beginning if not already present
        if 'All' not in states:
            states.insert(0, 'All')
        
        # Calculate initial performance data (default: monthly, all states)
        performance_data = get_bdm_performance(df, time_filter='monthly')
        print(f"Performance data entries: {len(performance_data)}")
        
        return render_template('dashboard.html', 
                               performance_data=performance_data,
                               months=months,
                               years=years,
                               states=states)
    except Exception as e:
        # Log the error but still render the page with default empty data
        print(f"Error rendering dashboard: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Provide fallback data for filters and empty performance data
        current_month = datetime.now().strftime('%B')
        current_year = datetime.now().year
        
        return render_template('dashboard.html',
                               performance_data=[],
                               months=[current_month],
                               years=[current_year],
                               states=['All'],
                               error_message=f"Error loading data: {str(e)}")

@app.route('/filter-data', methods=['POST'])
def filter_data():
    """Filter data based on the provided parameters"""
    try:
        # Get filter parameters
        time_filter = request.form.get('time_filter', 'monthly')
        month = request.form.get('month', '')
        year = request.form.get('year', '')
        state = request.form.get('state', 'All')
        start_date = request.form.get('start_date', None)
        end_date = request.form.get('end_date', None)
        
        # Check if this is essentially a "show all" request
        is_show_all = (
            (time_filter == 'monthly' and not month and not year) or
            (time_filter == 'daily' and not start_date) or
            (time_filter == 'weekly' and (not start_date or not end_date))
        ) and state == 'All'
        
        print(f"Filter request received: time={time_filter}, month={month}, year={year}, state={state}, start_date={start_date}, end_date={end_date}")
        print(f"Show all data: {is_show_all}")
        
        # Load data
        df = load_data()
        
        if df.empty:
            return jsonify({"error": "No data available"})
        
        # Apply filters
        performance_data = get_bdm_performance(df, time_filter, month, year, state, start_date, end_date)
        
        return jsonify(performance_data)
    except Exception as e:
        print(f"Error in filter_data route: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)