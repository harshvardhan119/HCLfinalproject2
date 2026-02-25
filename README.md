# 🇮🇳 Indian Stock Market Dashboard

## 🚀 Features

### 📊 Data & Analysis
- **Real-time stock data** fetching via Alpha Vantage API
- **15+ Indian stocks** pre-configured (Reliance, TCS, Infosys, HDFC, etc.)
- **Moving Averages** (SMA 20, 50, 200 + custom periods)
- **Exponential Moving Averages** (EMA 12, 26)
- **Bollinger Bands** (20-period, 2 std dev)
- **RSI (Relative Strength Index)** for momentum analysis
- **Daily Returns** percentage calculation

### 📈 Interactive Charts
- **Closing Price** with Moving Average overlays
- **Volume Analysis** with volume bar coloring & MA
- **Candlestick Charts** (OHLC)
- **Technical Indicators** panel (RSI, Daily Returns)

### 💾 Data Management
- **CSV Export** — download, save to disk, or archive with timestamp
- **CSV Import** — load previously saved data
- **File Manager** — view all saved CSV files

### ⏰ Automation
- **Auto-update scheduler** (APScheduler) with configurable intervals
- **Background data refresh** for watched stocks

### 📝 Production Quality
- **Structured logging** with daily log files + console output
- **Comprehensive unit tests** with pytest
- **Error handling** for API failures, timeouts, rate limits
- **Type hints** throughout the codebase

---

## 🛠️ Tech Stack

| Component          | Technology          |
|--------------------|---------------------|
| Language           | Python 3.9+         |
| Frontend           | Streamlit           |
| Charts             | Plotly              |
| Data Processing    | Pandas, NumPy       |
| API                | Alpha Vantage       |
| Scheduler          | APScheduler         |
| Testing            | Pytest              |
| Environment        | python-dotenv       |

---

## 📁 Project Structure

```
pythonproject/
├── app.py                     # Main Streamlit dashboard
├── config.py                  # Configuration settings
├── requirements.txt           # Python dependencies
├── .env                       # API key (create this)
├── .gitignore                 
├── README.md                  
├── src/
│   ├── __init__.py
│   ├── data_fetcher.py        # Alpha Vantage API client
│   ├── data_processor.py      # Technical indicators & analysis
│   ├── csv_handler.py         # CSV save/load operations
│   ├── scheduler.py           # Auto-update scheduler
│   └── logger.py              # Logging configuration
├── tests/
│   ├── __init__.py
│   ├── test_data_fetcher.py   # API client tests
│   ├── test_data_processor.py # Data processor tests
│   └── test_csv_handler.py    # CSV handler tests
├── data/                      # Saved CSV files
└── logs/                      # Log files
```

---

## ⚡ Quick Start

### 1. Clone & Navigate
```bash
cd pythonproject
```

### 2. Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API Key
Get your **free API key** from [Alpha Vantage](https://www.alphavantage.co/support/#api-key) and update `.env`:
```
ALPHA_VANTAGE_API_KEY=your_api_key_here
```

### 5. Run the Dashboard
```bash
streamlit run app.py
```

### 6. Run Tests
```bash
pytest tests/ -v
```

---

## 📸 Usage

1. **Select a stock** from the sidebar dropdown (15 Indian stocks available)
2. **Click "Fetch Data"** to load real-time stock data
3. **Explore tabs**: Closing Prices, Volume Trends, Candlestick, Technical Indicators
4. **Customize**: Toggle EMA, RSI, Bollinger Bands from the sidebar
5. **Export**: Download CSV, save to disk, or create timestamped archives
6. **Schedule**: Set auto-update intervals for continuous monitoring




