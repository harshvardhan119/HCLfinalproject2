"""Tests for CSV handling."""

import pytest
import pandas as pd
import numpy as np
import os
import tempfile

import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.csv_handler import CSVHandler


@pytest.fixture
def temp_data_dir():
    """Create a temporary directory for test CSV files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def csv_handler(temp_data_dir):
    """Create a CSVHandler with a temporary directory."""
    return CSVHandler(data_dir=temp_data_dir)


@pytest.fixture
def sample_df():
    """Create sample stock DataFrame."""
    dates = pd.date_range(start="2024-01-01", periods=10, freq="B")
    np.random.seed(42)

    df = pd.DataFrame(
        {
            "Open": np.random.uniform(2400, 2600, 10),
            "High": np.random.uniform(2500, 2700, 10),
            "Low": np.random.uniform(2300, 2500, 10),
            "Close": np.random.uniform(2400, 2600, 10),
            "Volume": np.random.randint(500000, 2000000, 10),
        },
        index=dates,
    )
    df.index.name = "Date"
    return df


class TestCSVHandler:

    def test_save_to_csv(self, csv_handler, sample_df):
        """Test saving DataFrame to CSV."""
        filepath = csv_handler.save_to_csv(sample_df, "RELIANCE.BSE")

        assert filepath is not None
        assert os.path.exists(filepath)
        assert filepath.endswith(".csv")

    def test_save_and_load_csv(self, csv_handler, sample_df):
        """Test round-trip save and load."""
        csv_handler.save_to_csv(sample_df, "RELIANCE.BSE")
        loaded_df = csv_handler.load_from_csv("RELIANCE.BSE")

        assert loaded_df is not None
        assert len(loaded_df) == len(sample_df)
        assert list(loaded_df.columns) == list(sample_df.columns)

    def test_save_empty_df(self, csv_handler):
        """Test saving empty DataFrame."""
        empty_df = pd.DataFrame()
        filepath = csv_handler.save_to_csv(empty_df, "EMPTY")

        assert filepath is None

    def test_save_none(self, csv_handler):
        """Test saving None."""
        filepath = csv_handler.save_to_csv(None, "NONE")

        assert filepath is None

    def test_load_nonexistent(self, csv_handler):
        """Test loading a non-existent file."""
        df = csv_handler.load_from_csv("NONEXISTENT")

        assert df is None

    def test_save_with_suffix(self, csv_handler, sample_df):
        """Test saving with custom suffix."""
        filepath = csv_handler.save_to_csv(
            sample_df, "RELIANCE.BSE", suffix="_daily"
        )

        assert filepath is not None
        assert "_daily" in filepath

    def test_list_saved_files(self, csv_handler, sample_df):
        """Test listing saved CSV files."""
        csv_handler.save_to_csv(sample_df, "RELIANCE.BSE")
        csv_handler.save_to_csv(sample_df, "TCS.BSE")

        files = csv_handler.list_saved_files()

        assert len(files) == 2
        assert all("filename" in f for f in files)
        assert all("size_kb" in f for f in files)

    def test_delete_csv(self, csv_handler, sample_df):
        """Test deleting a CSV file."""
        csv_handler.save_to_csv(sample_df, "RELIANCE.BSE")

        result = csv_handler.delete_csv("RELIANCE.BSE")

        assert result is True
        assert csv_handler.load_from_csv("RELIANCE.BSE") is None

    def test_delete_nonexistent(self, csv_handler):
        """Test deleting a non-existent file."""
        result = csv_handler.delete_csv("NONEXISTENT")

        assert result is False

    def test_export_with_timestamp(self, csv_handler, sample_df):
        """Test export with timestamp suffix."""
        filepath = csv_handler.export_with_timestamp(sample_df, "RELIANCE.BSE")

        assert filepath is not None
        assert os.path.exists(filepath)

    def test_data_integrity(self, csv_handler, sample_df):
        """Test that saved and loaded data values match."""
        csv_handler.save_to_csv(sample_df, "RELIANCE.BSE")
        loaded_df = csv_handler.load_from_csv("RELIANCE.BSE")

        pd.testing.assert_frame_equal(
            sample_df.round(6),
            loaded_df.round(6),
            check_freq=False,
            check_dtype=False,
        )
