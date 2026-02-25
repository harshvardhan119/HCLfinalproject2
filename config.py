"""
Configuration settings for the Indian Stock Market Dashboard.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Alpha Vantage API Configuration
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "demo")
ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"

# Popular Indian Stocks (NSE)
INDIAN_STOCKS = {
    "Reliance Industries": "RELIANCE.BSE",
    "Tata Consultancy Services": "TCS.BSE",
    "Infosys": "INFY.BSE",
    "HDFC Bank": "HDFCBANK.BSE",
    "ICICI Bank": "ICICIBANK.BSE",
    "State Bank of India": "SBIN.BSE",
    "Bharti Airtel": "BHARTIARTL.BSE",
    "ITC Limited": "ITC.BSE",
    "Kotak Mahindra Bank": "KOTAKBANK.BSE",
    "Hindustan Unilever": "HINDUNILVR.BSE",
    "Wipro": "WIPRO.BSE",
    "Asian Paints": "ASIANPAINT.BSE",
    "Maruti Suzuki": "MARUTI.BSE",
    "Titan Company": "TITAN.BSE",
    "Bajaj Finance": "BAJFINANCE.BSE",
}

# Data Storage
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
LOGS_DIR = os.path.join(os.path.dirname(__file__), "logs")

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# Moving Average Periods
MA_SHORT = 20
MA_MEDIUM = 50
MA_LONG = 200

# Scheduler Settings (in minutes)
AUTO_UPDATE_INTERVAL = 30
