"""Tests for data fetching using Yahoo Finance."""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_fetcher import StockDataFetcher

@pytest.fixture
def fetcher():
    """Create a StockDataFetcher instance."""
    return StockDataFetcher()

@pytest.fixture
def mock_history_data():
    """Sample history data."""
    dates = pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"])
    df = pd.DataFrame({
        "Open": [100.0, 101.0, 102.0],
        "High": [105.0, 106.0, 107.0],
        "Low": [95.0, 96.0, 97.0],
        "Close": [103.0, 104.0, 105.0],
        "Volume": [1000, 1100, 1200]
    }, index=dates)
    df.index.name = "Date"
    return df

class TestStockDataFetcher:

    @patch("yfinance.Ticker")
    def test_fetch_daily_data_success(self, mock_ticker, fetcher, mock_history_data):
        """Test successful daily data fetch."""
        mock_instance = MagicMock()
        mock_instance.history.return_value = mock_history_data
        mock_ticker.return_value = mock_instance

        df = fetcher.fetch_daily_stock_data("RELIANCE.NS")

        assert df is not None
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert list(df.columns) == ["Open", "High", "Low", "Close", "Volume"]

    @patch("yfinance.Ticker")
    def test_fetch_daily_data_empty(self, mock_ticker, fetcher):
        """Test handling of empty response."""
        mock_instance = MagicMock()
        mock_instance.history.return_value = pd.DataFrame()
        mock_ticker.return_value = mock_instance

        df = fetcher.fetch_daily_stock_data("INVALID")

        assert df is None

    @patch("yfinance.Ticker")
    def test_fetch_intraday_data_success(self, mock_ticker, fetcher, mock_history_data):
        """Test successful intraday data fetch."""
        mock_instance = MagicMock()
        mock_instance.history.return_value = mock_history_data
        mock_ticker.return_value = mock_instance

        df = fetcher.fetch_intraday_data("RELIANCE.NS", interval="5m")

        assert df is not None
        assert len(df) == 3

    @patch("yfinance.Ticker")
    def test_get_stock_overview_success(self, mock_ticker, fetcher):
        """Test successful company overview fetch."""
        mock_instance = MagicMock()
        mock_instance.info = {
            "longName": "Reliance Industries",
            "marketCap": 17000000000,
            "sector": "Energy",
            "industry": "Oil & Gas",
            "longBusinessSummary": "Summary text",
            "exchange": "NSE"
        }
        mock_ticker.return_value = mock_instance

        overview = fetcher.get_stock_overview("RELIANCE.NS")

        assert overview is not None
        assert overview["Name"] == "Reliance Industries"
        assert overview["Symbol"] == "RELIANCE.NS"

    @patch("yfinance.Ticker")
    def test_get_stock_overview_empty(self, mock_ticker, fetcher):
        """Test handling of empty overview response."""
        mock_instance = MagicMock()
        mock_instance.info = {}
        mock_ticker.return_value = mock_instance

        overview = fetcher.get_stock_overview("UNKNOWN")

        assert overview is None
