"""Stock market data fetching logic using Yahoo Finance."""

import pandas as pd
import yfinance as yf
from typing import Optional
from src.logger import logger
import requests
import random

class StockDataFetcher:
    """Robust Yahoo Finance Data Fetcher"""

    def __init__(self):
        """Initialize with multiple User-Agents to bypass blocks."""
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        ]

    def _get_session(self):
        """Create a new session with a random User-Agent."""
        session = requests.Session()
        session.headers.update({
            'User-Agent': random.choice(self.user_agents),
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
        })
        return session

    def fetch_daily_stock_data(
        self, symbol: str, output_size: str = "compact"
    ) -> Optional[pd.DataFrame]:
        """Fetch daily time series data."""
        period = "1y" if output_size == "compact" else "max"
        logger.info(f"Fetching daily data for {symbol} (period={period})")

        try:
            # Using yfinance download which is often more stable in cloud environments
            df = yf.download(
                tickers=symbol,
                period=period,
                interval="1d",
                progress=False,
                session=self._get_session(),
                timeout=20
            )

            if df is None or df.empty:
                logger.error(f"No data found for {symbol}")
                return None

            # Flatten multi-index if it exists (happens with some yfinance versions)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            # Standardize index
            df.index = pd.to_datetime(df.index).tz_localize(None)
            df.index.name = "Date"
            
            # Select essential columns and ensure they are numeric
            cols = ["Open", "High", "Low", "Close", "Volume"]
            df = df[cols].apply(pd.to_numeric, errors='coerce')
            
            # Drop any rows with NaN in Close
            df = df.dropna(subset=['Close'])

            logger.info(f"Successfully fetched {len(df)} records for {symbol}")
            return df

        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return None

    def fetch_intraday_data(
        self, symbol: str, interval: str = "5m"
    ) -> Optional[pd.DataFrame]:
        """Fetch intraday prices."""
        if "min" in interval:
            interval = interval.replace("min", "m")
        
        logger.info(f"Fetching intraday data for {symbol} (interval={interval})")

        try:
            df = yf.download(
                tickers=symbol,
                period="5d",
                interval=interval,
                progress=False,
                session=self._get_session(),
                timeout=20
            )

            if df is None or df.empty:
                logger.error(f"No intraday data found for {symbol}")
                return None

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            df.index = pd.to_datetime(df.index).tz_localize(None)
            cols = ["Open", "High", "Low", "Close", "Volume"]
            df = df[cols].apply(pd.to_numeric, errors='coerce')
            
            logger.info(f"Successfully fetched {len(df)} intraday records for {symbol}")
            return df

        except Exception as e:
            logger.error(f"Error fetching intraday data for {symbol}: {e}")
            return None

    def get_stock_overview(self, symbol: str) -> Optional[dict]:
        """Fetch company fundamentals."""
        logger.info(f"Fetching company overview for {symbol}")

        try:
            ticker = yf.Ticker(symbol, session=self._get_session())
            info = ticker.info
            
            # If info is blocked or empty, provide a graceful fallback
            if not info or len(info) < 5:
                return {
                    "Symbol": symbol,
                    "Name": symbol.split('.')[0],
                    "MarketCapitalization": "N/A",
                    "Sector": "N/A",
                    "Industry": "N/A",
                    "Description": "Overview temporarily unavailable (API limits). Charts still work!",
                }

            return {
                "Symbol": symbol,
                "Name": info.get("longName", info.get("shortName", symbol)),
                "MarketCapitalization": info.get("marketCap"),
                "Sector": info.get("sector"),
                "Industry": info.get("industry"),
                "Description": info.get("longBusinessSummary", "N/A"),
                "Exchange": info.get("exchange"),
                "Currency": info.get("currency")
            }

        except Exception as e:
            logger.error(f"Failed to fetch overview for {symbol}: {e}")
            # Even on error, return something so the UI doesn't crash
            return {
                "Symbol": symbol,
                "Name": symbol.split('.')[0],
                "Description": "Overview currently unavailable. Please check the charts instead.",
            }
