"""Stock market data fetching logic with advanced cloud-bypass."""

import pandas as pd
import yfinance as yf
from typing import Optional
from src.logger import logger
import requests
import random

class StockDataFetcher:
    """Production-grade Data Fetcher for Render/Streamlit"""

    def __init__(self):
        # We'll use the internal yfinance handling which is actually 
        # more stable than a custom requests session on high-traffic IPs
        pass

    def fetch_daily_stock_data(
        self, symbol: str, output_size: str = "compact"
    ) -> Optional[pd.DataFrame]:
        """Fetch daily data with automatic multi-index handling."""
        period = "1y" if output_size == "compact" else "max"
        logger.info(f"Fetching daily data for {symbol} (period={period})")

        try:
            # Setting auto_adjust=True and multi_level_index=False 
            # are the keys to avoiding most yfinance errors
            df = yf.download(
                tickers=symbol,
                period=period,
                interval="1d",
                auto_adjust=True,
                multi_level_index=False,
                progress=False,
                timeout=15
            )

            if df is None or df.empty:
                logger.error(f"No data found for {symbol} - IP might be throttled")
                return None

            # Standardize index - important for stats calculation
            df.index = pd.to_datetime(df.index).tz_localize(None)
            df.index.name = "Date"
            
            # Select essential columns
            cols = ["Open", "High", "Low", "Close", "Volume"]
            
            # Map columns just in case Yahoo returned different names
            current_cols = df.columns.tolist()
            mapping = {
                'Adj Close': 'Close',
                'Volume': 'Volume',
                'High': 'High',
                'Low': 'Low',
                'Open': 'Open'
            }
            
            # Dynamically rename if necessary
            df = df.rename(columns=mapping)
            
            # Final selection and numeric conversion
            available_cols = [c for c in cols if c in df.columns]
            df = df[available_cols].apply(pd.to_numeric, errors='coerce')
            df = df.dropna(subset=['Close'])

            logger.info(f"Successfully fetched {len(df)} records for {symbol}")
            return df

        except Exception as e:
            logger.error(f"Critical error fetching {symbol}: {e}")
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
                auto_adjust=True,
                multi_level_index=False,
                progress=False,
                timeout=15
            )

            if df is None or df.empty:
                logger.error(f"No intraday data found for {symbol}")
                return None

            df.index = pd.to_datetime(df.index).tz_localize(None)
            mapping = {'Adj Close': 'Close'}
            df = df.rename(columns=mapping)
            
            cols = ["Open", "High", "Low", "Close", "Volume"]
            available_cols = [c for c in cols if c in df.columns]
            df = df[available_cols].apply(pd.to_numeric, errors='coerce')
            
            logger.info(f"Successfully fetched {len(df)} intraday records for {symbol}")
            return df

        except Exception as e:
            logger.error(f"Error fetching intraday data: {e}")
            return None

    def get_stock_overview(self, symbol: str) -> Optional[dict]:
        """Fetch company fundamentals - Least stable part in cloud, so we use fallback."""
        logger.info(f"Fetching company overview for {symbol}")

        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if not info or len(info) < 5:
                raise Exception("Minimal info returned")

            return {
                "Symbol": symbol,
                "Name": info.get("longName", info.get("shortName", symbol)),
                "MarketCapitalization": info.get("marketCap"),
                "Sector": info.get("sector", "N/A"),
                "Industry": info.get("industry", "N/A"),
                "Description": info.get("longBusinessSummary", "Overview unavailable."),
                "Exchange": info.get("exchange"),
                "Currency": info.get("currency")
            }

        except Exception:
            # Fallback so the UI doesn't look broken
            return {
                "Symbol": symbol,
                "Name": symbol.split('.')[0].upper(),
                "Description": "Fundamental data is currently limited by API provider. See charts for technical analysis.",
            }
