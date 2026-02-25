"""Tests for data fetching."""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_fetcher import StockDataFetcher


@pytest.fixture
def fetcher():
    """Create a StockDataFetcher instance with a test API key."""
    return StockDataFetcher(api_key="test_api_key")


@pytest.fixture
def mock_daily_response():
    """Sample daily time series API response."""
    return {
        "Meta Data": {
            "1. Information": "Daily Prices",
            "2. Symbol": "RELIANCE.BSE",
        },
        "Time Series (Daily)": {
            "2024-01-05": {
                "1. open": "2500.00",
                "2. high": "2550.00",
                "3. low": "2480.00",
                "4. close": "2530.00",
                "5. volume": "1000000",
            },
            "2024-01-04": {
                "1. open": "2480.00",
                "2. high": "2510.00",
                "3. low": "2470.00",
                "4. close": "2500.00",
                "5. volume": "900000",
            },
            "2024-01-03": {
                "1. open": "2450.00",
                "2. high": "2490.00",
                "3. low": "2440.00",
                "4. close": "2480.00",
                "5. volume": "850000",
            },
        },
    }


class TestStockDataFetcher:

    @patch("src.data_fetcher.requests.Session.get")
    def test_fetch_daily_data_success(self, mock_get, fetcher, mock_daily_response):
        """Test successful daily data fetch."""
        mock_response = MagicMock()
        mock_response.json.return_value = mock_daily_response
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        df = fetcher.fetch_daily_stock_data("RELIANCE.BSE")

        assert df is not None
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert list(df.columns) == ["Open", "High", "Low", "Close", "Volume"]
        assert df.index.is_monotonic_increasing  # Sorted ascending

    @patch("src.data_fetcher.requests.Session.get")
    def test_fetch_daily_data_api_error(self, mock_get, fetcher):
        """Test handling of API error messages."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "Error Message": "Invalid API call."
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        df = fetcher.fetch_daily_stock_data("INVALID")

        assert df is None

    @patch("src.data_fetcher.requests.Session.get")
    def test_fetch_daily_data_rate_limit(self, mock_get, fetcher):
        """Test handling of API rate limiting."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "Note": "Thank you for using Alpha Vantage! API call frequency limit reached."
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        df = fetcher.fetch_daily_stock_data("RELIANCE.BSE")

        assert df is None

    @patch("src.data_fetcher.requests.Session.get")
    def test_fetch_daily_data_timeout(self, mock_get, fetcher):
        """Test handling of request timeout."""
        import requests

        mock_get.side_effect = requests.exceptions.Timeout("Connection timed out")

        df = fetcher.fetch_daily_stock_data("RELIANCE.BSE")

        assert df is None

    @patch("src.data_fetcher.requests.Session.get")
    def test_fetch_daily_data_connection_error(self, mock_get, fetcher):
        """Test handling of connection errors."""
        import requests

        mock_get.side_effect = requests.exceptions.ConnectionError("No internet")

        df = fetcher.fetch_daily_stock_data("RELIANCE.BSE")

        assert df is None

    @patch("src.data_fetcher.requests.Session.get")
    def test_fetch_daily_data_numeric_conversion(
        self, mock_get, fetcher, mock_daily_response
    ):
        """Test that data is properly converted to numeric types."""
        mock_response = MagicMock()
        mock_response.json.return_value = mock_daily_response
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        df = fetcher.fetch_daily_stock_data("RELIANCE.BSE")

        assert df["Close"].dtype in ["float64", "int64"]
        assert df["Volume"].dtype in ["float64", "int64"]

    @patch("src.data_fetcher.requests.Session.get")
    def test_fetch_daily_data_info_message(self, mock_get, fetcher):
        """Test handling of API information messages."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "Information": "Please subscribe to premium plan."
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        df = fetcher.fetch_daily_stock_data("RELIANCE.BSE")

        assert df is None

    @patch("src.data_fetcher.requests.Session.get")
    def test_fetch_intraday_data_success(self, mock_get, fetcher):
        """Test successful intraday data fetch."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "Meta Data": {"1. Information": "Intraday Prices"},
            "Time Series (5min)": {
                "2024-01-05 10:00:00": {
                    "1. open": "2500.00",
                    "2. high": "2510.00",
                    "3. low": "2495.00",
                    "4. close": "2505.00",
                    "5. volume": "50000",
                }
            },
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        df = fetcher.fetch_intraday_data("RELIANCE.BSE", interval="5min")

        assert df is not None
        assert len(df) == 1

    @patch("src.data_fetcher.requests.Session.get")
    def test_get_stock_overview_success(self, mock_get, fetcher):
        """Test successful company overview fetch."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "Symbol": "RELIANCE.BSE",
            "Name": "Reliance Industries",
            "MarketCapitalization": "17000000000",
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        overview = fetcher.get_stock_overview("RELIANCE.BSE")

        assert overview is not None
        assert overview["Symbol"] == "RELIANCE.BSE"

    @patch("src.data_fetcher.requests.Session.get")
    def test_get_stock_overview_empty(self, mock_get, fetcher):
        """Test handling of empty overview response."""
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        overview = fetcher.get_stock_overview("UNKNOWN")

        assert overview is None
