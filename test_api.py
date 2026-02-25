import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
print(f"API Key found: {api_key is not None}")

url = "https://www.alphavantage.co/query"
params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": "RELIANCE.BSE",
    "apikey": api_key
}

response = requests.get(url, params=params)
data = response.json()

if "Note" in data:
    print("RATE LIMIT REACHED:", data["Note"])
elif "Error Message" in data:
    print("API ERROR:", data["Error Message"])
elif "Time Series (Daily)" in data:
    print("SUCCESS: Data fetched.")
else:
    print("OTHER RESPONSE:", data.keys())
