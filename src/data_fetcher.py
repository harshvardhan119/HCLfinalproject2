"""Stock market data fetching logic."""

import requests
import pandas as pd
from typing import Optional

from config import ALPHA_VANTAGE_API_KEY, ALPHA_VANTAGE_BASE_URL
from src.logger import logger


class StockDataFetcher:
    """NSE/BSE Data Fetcher"""

    def __init__(self, api_key: str = ALPHA_VANTAGE_API_KEY):
        self.api_key = api_key
        self.base_url = ALPHA_VANTAGE_BASE_URL
        self.session = requests.Session()

    def fetch_daily_stock_data(
        self, symbol: str, output_size: str = "compact"
    ) -> Optional[pd.DataFrame]:
        """Fetch daily time series data."""
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "outputsize": output_size,
            "apikey": self.api_key,
        }

        logger.info(f"Fetching daily data for {symbol} (output_size={output_size})")

        try:
            response = self.session.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            # Check for API error messages
            if "Error Message" in data:
                logger.error(f"API Error for {symbol}: {data['Error Message']}")
                return None

            if "Note" in data:
                logger.warning(f"API Rate Limit Warning: {data['Note']}")
                return None

            if "Information" in data:
                logger.warning(f"API Info: {data['Information']}")
                return None

            time_series_key = "Time Series (Daily)"
            if time_series_key not in data:
                logger.error(
                    f"Unexpected response format for {symbol}. Keys: {list(data.keys())}"
                )
                return None

            # Parse the time series data
            df = pd.DataFrame.from_dict(data[time_series_key], orient="index")
            df.index = pd.to_datetime(df.index)
            df.index.name = "Date"

            # Rename columns
            df.columns = ["Open", "High", "Low", "Close", "Volume"]

            # Convert to numeric types
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

            # Sort by date (ascending)
            df.sort_index(inplace=True)

            logger.info(
                f"Successfully fetched {len(df)} records for {symbol}"
            )
            return df

        except requests.exceptions.Timeout:
            logger.error(f"Request timeout while fetching data for {symbol}")
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error while fetching data for {symbol}")
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error for {symbol}: {e}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {symbol}: {e}")
            return None
        except (ValueError, KeyError) as e:
            logger.error(f"Data parsing error for {symbol}: {e}")
            return None

    def fetch_intraday_data(
        self, symbol: str, interval: str = "5min"
    ) -> Optional[pd.DataFrame]:
        """Fetch intraday prices."""
        params = {
            "function": "TIME_SERIES_INTRADAY",
            "symbol": symbol,
            "interval": interval,
            "apikey": self.api_key,
        }

        logger.info(f"Fetching intraday data for {symbol} (interval={interval})")

        try:
            response = self.session.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            if "Error Message" in data:
                logger.error(f"API Error for {symbol}: {data['Error Message']}")
                return None

            if "Note" in data:
                logger.warning(f"API Rate Limit Warning: {data['Note']}")
                return None

            if "Information" in data:
                logger.warning(f"API Info: {data['Information']}")
                return None

            time_series_key = f"Time Series ({interval})"
            if time_series_key not in data:
                logger.error(
                    f"Unexpected response for {symbol}. Keys: {list(data.keys())}"
                )
                return None

            df = pd.DataFrame.from_dict(data[time_series_key], orient="index")
            df.index = pd.to_datetime(df.index)
            df.index.name = "Datetime"

            df.columns = ["Open", "High", "Low", "Close", "Volume"]

            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

            df.sort_index(inplace=True)

            logger.info(
                f"Successfully fetched {len(df)} intraday records for {symbol}"
            )
            return df

        except requests.exceptions.Timeout:
            logger.error(f"Timeout fetching intraday data for {symbol}")
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error fetching intraday data for {symbol}")
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error for intraday {symbol}: {e}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for intraday {symbol}: {e}")
            return None
        except (ValueError, KeyError) as e:
            logger.error(f"Parsing error for intraday {symbol}: {e}")
            return None

    def get_stock_overview(self, symbol: str) -> Optional[dict]:
        """Fetch company fundamentals."""
        params = {
            "function": "OVERVIEW",
            "symbol": symbol,
            "apikey": self.api_key,
        }

        logger.info(f"Fetching company overview for {symbol}")

        try:
            response = self.session.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            if not data or "Symbol" not in data:
                logger.warning(f"No overview data available for {symbol}")
                return None

            logger.info(f"Successfully fetched overview for {symbol}")
            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch overview for {symbol}: {e}")
            return None
