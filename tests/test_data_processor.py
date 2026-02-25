"""Tests for data processing."""

import pytest
import pandas as pd
import numpy as np

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_processor import StockDataProcessor


@pytest.fixture
def sample_stock_data():
    """Create sample stock data for testing."""
    dates = pd.date_range(start="2024-01-01", periods=60, freq="B")
    np.random.seed(42)

    base_price = 2500
    prices = base_price + np.cumsum(np.random.randn(60) * 10)

    df = pd.DataFrame(
        {
            "Open": prices - np.random.rand(60) * 5,
            "High": prices + np.random.rand(60) * 15,
            "Low": prices - np.random.rand(60) * 15,
            "Close": prices,
            "Volume": np.random.randint(500000, 2000000, size=60),
        },
        index=dates,
    )
    df.index.name = "Date"
    return df


@pytest.fixture
def processor():
    """Create a StockDataProcessor instance."""
    return StockDataProcessor()


class TestStockDataProcessor:

    def test_calculate_moving_averages_default(self, processor, sample_stock_data):
        """Test default moving average calculation."""
        result = processor.calculate_moving_averages(sample_stock_data)

        assert "SMA_20" in result.columns
        assert "SMA_50" in result.columns
        assert "SMA_200" in result.columns

    def test_calculate_moving_averages_custom_periods(
        self, processor, sample_stock_data
    ):
        """Test custom period moving averages."""
        result = processor.calculate_moving_averages(
            sample_stock_data, periods=[5, 10]
        )

        assert "SMA_5" in result.columns
        assert "SMA_10" in result.columns
        assert "SMA_20" not in result.columns

    def test_calculate_moving_averages_values(self, processor, sample_stock_data):
        """Test that MA values are correctly calculated."""
        result = processor.calculate_moving_averages(
            sample_stock_data, periods=[5]
        )

        # Check a specific SMA_5 value (manual calculation)
        expected = sample_stock_data["Close"].iloc[:5].mean()
        actual = result["SMA_5"].iloc[4]

        assert abs(expected - actual) < 0.001

    def test_calculate_moving_averages_empty_df(self, processor):
        """Test MA with empty DataFrame."""
        empty_df = pd.DataFrame()
        result = processor.calculate_moving_averages(empty_df)

        assert result is not None

    def test_calculate_moving_averages_none(self, processor):
        """Test MA with None input."""
        result = processor.calculate_moving_averages(None)

        assert result is None

    def test_calculate_ema(self, processor, sample_stock_data):
        """Test EMA calculation."""
        result = processor.calculate_ema(sample_stock_data)

        assert "EMA_12" in result.columns
        assert "EMA_26" in result.columns
        assert not result["EMA_12"].isna().all()

    def test_calculate_ema_custom_periods(self, processor, sample_stock_data):
        """Test custom EMA periods."""
        result = processor.calculate_ema(sample_stock_data, periods=[9, 21])

        assert "EMA_9" in result.columns
        assert "EMA_21" in result.columns

    def test_calculate_rsi(self, processor, sample_stock_data):
        """Test RSI calculation."""
        result = processor.calculate_rsi(sample_stock_data)

        assert "RSI" in result.columns

        # RSI should be between 0 and 100
        valid_rsi = result["RSI"].dropna()
        assert (valid_rsi >= 0).all()
        assert (valid_rsi <= 100).all()

    def test_calculate_bollinger_bands(self, processor, sample_stock_data):
        """Test Bollinger Bands calculation."""
        result = processor.calculate_bollinger_bands(sample_stock_data)

        assert "BB_Upper" in result.columns
        assert "BB_Middle" in result.columns
        assert "BB_Lower" in result.columns

        # Upper band should always be >= Middle >= Lower
        valid_idx = result["BB_Upper"].dropna().index
        assert (
            result.loc[valid_idx, "BB_Upper"] >= result.loc[valid_idx, "BB_Middle"]
        ).all()
        assert (
            result.loc[valid_idx, "BB_Middle"] >= result.loc[valid_idx, "BB_Lower"]
        ).all()

    def test_calculate_daily_returns(self, processor, sample_stock_data):
        """Test daily returns calculation."""
        result = processor.calculate_daily_returns(sample_stock_data)

        assert "Daily_Return" in result.columns
        assert pd.isna(result["Daily_Return"].iloc[0])  # First value should be NaN

    def test_calculate_volume_ma(self, processor, sample_stock_data):
        """Test volume moving average calculation."""
        result = processor.calculate_volume_ma(sample_stock_data, period=10)

        assert "Volume_MA" in result.columns
        assert not result["Volume_MA"].iloc[10:].isna().any()

    def test_get_summary_statistics(self, processor, sample_stock_data):
        """Test summary statistics generation."""
        stats = processor.get_summary_statistics(sample_stock_data)

        assert "latest_close" in stats
        assert "latest_open" in stats
        assert "period_high" in stats
        assert "period_low" in stats
        assert "avg_volume" in stats
        assert "total_records" in stats
        assert "price_change" in stats
        assert "price_change_pct" in stats
        assert stats["total_records"] == 60

    def test_get_summary_statistics_empty(self, processor):
        """Test summary stats with empty DataFrame."""
        stats = processor.get_summary_statistics(pd.DataFrame())

        assert stats == {}

    def test_original_data_not_modified(self, processor, sample_stock_data):
        """Test that original DataFrame is not modified by processors."""
        original_columns = list(sample_stock_data.columns)

        processor.calculate_moving_averages(sample_stock_data)
        processor.calculate_rsi(sample_stock_data)

        assert list(sample_stock_data.columns) == original_columns
