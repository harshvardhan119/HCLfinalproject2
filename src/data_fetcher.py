"""Stock market data fetching logic using Yahoo Finance."""

import pandas as pd
import yfinance as yf
from typing import Optional
from src.logger import logger

import requests

class StockDataFetcher:
    """Yahoo Finance Data Fetcher"""

    def __init__(self):
        """Initialize the fetcher with browser-like headers."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Origin': 'https://finance.yahoo.com',
            'Referer': 'https://finance.yahoo.com'
        })

    def fetch_daily_stock_data(
        self, symbol: str, output_size: str = "compact"
    ) -> Optional[pd.DataFrame]:
        """
        Fetch daily time series data.
        Maps Alpha Vantage 'output_size' to yfinance periods:
        - compact -> 1y
        - full -> max
        """
        period = "1y" if output_size == "compact" else "max"
        logger.info(f"Fetching daily data for {symbol} (output_size={output_size} -> period={period})")

        try:
            ticker = yf.Ticker(symbol, session=self.session)
            df = ticker.history(period=period)

            if df.empty:
                logger.error(f"No data found for {symbol}")
                return None

            # Standardize columns: yfinance might return timezone-aware or different index
            if df.index.name != "Date":
                df.index.name = "Date"
            
            # Ensure index is DatetimeIndex and remove timezone info
            df.index = pd.to_datetime(df.index).tz_localize(None)
            
            # Select essential columns
            cols_to_keep = ["Open", "High", "Low", "Close", "Volume"]
            df = df[cols_to_keep]
            
            # Convert to numeric-only to be safe
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

            logger.info(f"Successfully fetched {len(df)} records for {symbol}")
            return df

        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return None

    def fetch_intraday_data(
        self, symbol: str, interval: str = "5m"
    ) -> Optional[pd.DataFrame]:
        """Fetch intraday prices."""
        # yfinance interval mapping: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
        # Alpha Vantage uses "5min", "1min", etc.
        if "min" in interval:
            interval = interval.replace("min", "m")
        
        logger.info(f"Fetching intraday data for {symbol} (interval={interval})")

        try:
            ticker = yf.Ticker(symbol, session=self.session)
            # Fetch last 5 days for intraday
            df = ticker.history(period="5d", interval=interval)

            if df.empty:
                logger.error(f"No intraday data found for {symbol}")
                return None

            # Standardize index
            df.index = pd.to_datetime(df.index).tz_localize(None)
            
            # Standardize columns
            cols_to_keep = ["Open", "High", "Low", "Close", "Volume"]
            df = df[cols_to_keep]
            
            logger.info(f"Successfully fetched {len(df)} intraday records for {symbol}")
            return df

        except Exception as e:
            logger.error(f"Error fetching intraday data for {symbol}: {e}")
            return None

    def get_stock_overview(self, symbol: str) -> Optional[dict]:
        """Fetch company fundamentals."""
        logger.info(f"Fetching company overview for {symbol}")

        try:
            ticker = yf.Ticker(symbol, session=self.session)
            info = ticker.info
            
            if not info or len(info) < 5: # Some limited info might still exist
                logger.warning(f"No overview data available for {symbol}")
                return None

            # Standardize keys for compatibility with app.py
            standardized_info = {
                "Symbol": symbol,
                "Name": info.get("longName", info.get("shortName", symbol)),
                "MarketCapitalization": info.get("marketCap"),
                "Sector": info.get("sector"),
                "Industry": info.get("industry"),
                "Description": info.get("longBusinessSummary", "N/A"),
                "Exchange": info.get("exchange"),
                "Currency": info.get("currency")
            }

            logger.info(f"Successfully fetched overview for {symbol}")
            return standardized_info

        except Exception as e:
            logger.error(f"Failed to fetch overview for {symbol}: {e}")
            return None
