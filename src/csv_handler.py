"""
CSV Handler module for the Indian Stock Market Dashboard.
Handles saving and loading stock data to/from CSV files.
"""

import os
import pandas as pd
from datetime import datetime
from typing import Optional

from config import DATA_DIR
from src.logger import logger


class CSVHandler:
    """Handles CSV file operations for stock data persistence."""

    def __init__(self, data_dir: str = DATA_DIR):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)

    def _get_filepath(self, symbol: str, suffix: str = "") -> str:
        """Generate a standardized file path for a stock symbol."""
        clean_symbol = symbol.replace(".", "_").replace("/", "_")
        filename = f"{clean_symbol}{suffix}.csv"
        return os.path.join(self.data_dir, filename)

    def save_to_csv(
        self, df: pd.DataFrame, symbol: str, suffix: str = ""
    ) -> Optional[str]:
        """
        Save DataFrame to a CSV file.

        Args:
            df: DataFrame to save.
            symbol: Stock symbol (used in filename).
            suffix: Optional suffix for the filename.

        Returns:
            File path of saved CSV, or None if save fails.
        """
        if df is None or df.empty:
            logger.warning(f"No data to save for {symbol}")
            return None

        filepath = self._get_filepath(symbol, suffix)

        try:
            df.to_csv(filepath)
            logger.info(
                f"Data saved to {filepath} ({len(df)} records)"
            )
            return filepath
        except (IOError, OSError) as e:
            logger.error(f"Failed to save CSV for {symbol}: {e}")
            return None

    def load_from_csv(self, symbol: str, suffix: str = "") -> Optional[pd.DataFrame]:
        """
        Load DataFrame from a CSV file.

        Args:
            symbol: Stock symbol (used to find file).
            suffix: Optional suffix for the filename.

        Returns:
            DataFrame with stock data, or None if file not found.
        """
        filepath = self._get_filepath(symbol, suffix)

        if not os.path.exists(filepath):
            logger.info(f"No cached CSV found for {symbol} at {filepath}")
            return None

        try:
            df = pd.read_csv(filepath, index_col=0, parse_dates=True)
            logger.info(
                f"Loaded {len(df)} records from {filepath}"
            )
            return df
        except (IOError, pd.errors.EmptyDataError) as e:
            logger.error(f"Failed to load CSV for {symbol}: {e}")
            return None

    def list_saved_files(self) -> list:
        """
        List all saved CSV files in the data directory.

        Returns:
            List of dictionaries with file info.
        """
        files = []
        try:
            for filename in os.listdir(self.data_dir):
                if filename.endswith(".csv"):
                    filepath = os.path.join(self.data_dir, filename)
                    stat = os.stat(filepath)
                    files.append(
                        {
                            "filename": filename,
                            "filepath": filepath,
                            "size_kb": round(stat.st_size / 1024, 2),
                            "modified": datetime.fromtimestamp(
                                stat.st_mtime
                            ).strftime("%Y-%m-%d %H:%M:%S"),
                        }
                    )
        except OSError as e:
            logger.error(f"Error listing saved files: {e}")

        return files

    def delete_csv(self, symbol: str, suffix: str = "") -> bool:
        """
        Delete a saved CSV file.

        Args:
            symbol: Stock symbol.
            suffix: Optional suffix.

        Returns:
            True if deleted, False otherwise.
        """
        filepath = self._get_filepath(symbol, suffix)

        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                logger.info(f"Deleted CSV: {filepath}")
                return True
            except OSError as e:
                logger.error(f"Failed to delete {filepath}: {e}")
                return False

        logger.warning(f"File not found for deletion: {filepath}")
        return False

    def export_with_timestamp(
        self, df: pd.DataFrame, symbol: str
    ) -> Optional[str]:
        """
        Export data with a timestamp suffix for archival.

        Args:
            df: DataFrame to export.
            symbol: Stock symbol.

        Returns:
            File path of exported CSV.
        """
        timestamp = datetime.now().strftime("_%Y%m%d_%H%M%S")
        return self.save_to_csv(df, symbol, suffix=timestamp)
