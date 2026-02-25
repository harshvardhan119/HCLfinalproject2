"""Stock market data fetching logic using Yahoo Finance."""

import pandas as pd
import yfinance as yf
from typing import Optional
from src.logger import logger
import requests
import time

class StockDataFetcher:
    """Yahoo Finance Data Fetcher with Cloud-Bypass Handshake"""

    def __init__(self):
        """Initialize the fetcher with browser-like headers and session."""
        self.session = requests.Session()
        # Using a very recent Chrome User-Agent
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Origin': 'https://finance.yahoo.com',
            'Referer': 'https://finance.yahoo.com'
        })
        # Pre-emptive handshake to get cookies
        try:
            self.session.get("https://fc.yahoo.com", timeout=10)
        except:
            pass

    def fetch_daily_stock_data(
        self, symbol: str, output_size: str = "compact"
    ) -> Optional[pd.DataFrame]:
        """Fetch daily time series data."""
        period = "1y" if output_size == "compact" else "max"
        logger.info(f"Fetching daily data for {symbol} (period={period})")

        try:
            # Re-verify session occasionally to avoid expiration
            ticker = yf.Ticker(symbol, session=self.session)
            df = ticker.history(period=period)

            if df.empty:
                logger.error(f"No data found for {symbol}")
                return None

            # Standardize index
            df.index = pd.to_datetime(df.index).tz_localize(None)
            df.index.name = "Date"
            
            # Select essential columns
            cols_to_keep = ["Open", "High", "Low", "Close", "Volume"]
            df = df[cols_to_keep]
            
            # Convert to numeric-only
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

            logger.info(f"Successfully fetched {len(df)} records for {symbol}")
            return df

        except Exception as e:
            if "Too Many Requests" in str(e) or "429" in str(e):
                logger.error(f"Yahoo Finance Rate Limit (429) on {symbol}. Cloud IP might be flagged.")
            else:
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
            ticker = yf.Ticker(symbol, session=self.session)
            df = ticker.history(period="5d", interval=interval)

            if df.empty:
                logger.error(f"No intraday data found for {symbol}")
                return None

            df.index = pd.to_datetime(df.index).tz_localize(None)
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
            
            if not info or len(info) < 5:
                # Fallback for name if full info is blocked
                return {
                    "Symbol": symbol,
                    "Name": symbol.split('.')[0],
                    "MarketCapitalization": "N/A",
                    "Sector": "N/A",
                    "Industry": "N/A",
                    "Description": "Detailed overview unavailable due to API limits.",
                }

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
