# Configuration settings for the BDM Dashboard application
import os

class Config:
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    
    # Data file path
    DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'bdm_data.csv')
    
    # Date format
    DATE_FORMAT = '%d-%m-%Y %H:%M'
    
    # List of all Indian states for filters
    STATES = [
        "ANDHRA PRADESH", "ARUNACHAL PRADESH", "ASSAM", "BIHAR", "CHHATTISGARH", "GOA", "GUJARAT", 
        "HARYANA", "HIMACHAL PRADESH", "JHARKHAND", "KARNATAKA", "KERALA", "MADHYA PRADESH", 
        "MAHARASHTRA", "MANIPUR", "MEGHALAYA", "MIZORAM", "NAGALAND", "ODISHA", "PUNJAB", 
        "RAJASTHAN", "SIKKIM", "TAMIL NADU", "TELANGANA", "TRIPURA", "UTTAR PRADESH", 
        "UTTARAKHAND", "WEST BENGAL"
    ]