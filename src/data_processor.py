"""
Data Processor module for the Indian Stock Market Dashboard.
Handles data transformations: moving averages, technical indicators, etc.
"""

import pandas as pd
from typing import List, Optional

from src.logger import logger
from config import MA_SHORT, MA_MEDIUM, MA_LONG


class StockDataProcessor:
    """Processes stock data for analysis and visualization."""

    @staticmethod
    def calculate_moving_averages(
        df: pd.DataFrame,
        periods: Optional[List[int]] = None,
        column: str = "Close",
    ) -> pd.DataFrame:
        """
        Calculate Simple Moving Averages (SMA) for given periods.

        Args:
            df: DataFrame with stock data.
            periods: List of MA periods. Defaults to [20, 50, 200].
            column: Column to calculate MA on.

        Returns:
            DataFrame with added MA columns.
        """
        if df is None or df.empty:
            logger.warning("Empty DataFrame passed to calculate_moving_averages")
            return df

        if periods is None:
            periods = [MA_SHORT, MA_MEDIUM, MA_LONG]

        result = df.copy()

        for period in periods:
            col_name = f"SMA_{period}"
            result[col_name] = result[column].rolling(window=period).mean()
            logger.debug(f"Calculated {col_name} for {column}")

        logger.info(f"Moving averages calculated: {[f'SMA_{p}' for p in periods]}")
        return result

    @staticmethod
    def calculate_ema(
        df: pd.DataFrame,
        periods: Optional[List[int]] = None,
        column: str = "Close",
    ) -> pd.DataFrame:
        """
        Calculate Exponential Moving Averages (EMA).

        Args:
            df: DataFrame with stock data.
            periods: List of EMA periods. Defaults to [12, 26].
            column: Column to calculate EMA on.

        Returns:
            DataFrame with added EMA columns.
        """
        if df is None or df.empty:
            logger.warning("Empty DataFrame passed to calculate_ema")
            return df

        if periods is None:
            periods = [12, 26]

        result = df.copy()

        for period in periods:
            col_name = f"EMA_{period}"
            result[col_name] = result[column].ewm(span=period, adjust=False).mean()
            logger.debug(f"Calculated {col_name}")

        return result

    @staticmethod
    def calculate_rsi(
        df: pd.DataFrame, period: int = 14, column: str = "Close"
    ) -> pd.DataFrame:
        """
        Calculate Relative Strength Index (RSI).

        Args:
            df: DataFrame with stock data.
            period: RSI lookback period.
            column: Column to calculate RSI on.

        Returns:
            DataFrame with added RSI column.
        """
        if df is None or df.empty:
            logger.warning("Empty DataFrame passed to calculate_rsi")
            return df

        result = df.copy()
        delta = result[column].diff()

        gain = delta.where(delta > 0, 0)
        loss = (-delta).where(delta < 0, 0)

        avg_gain = gain.rolling(window=period, min_periods=1).mean()
        avg_loss = loss.rolling(window=period, min_periods=1).mean()

        rs = avg_gain / avg_loss
        result["RSI"] = 100 - (100 / (1 + rs))

        logger.info(f"RSI calculated with period={period}")
        return result

    @staticmethod
    def calculate_bollinger_bands(
        df: pd.DataFrame, period: int = 20, std_dev: int = 2, column: str = "Close"
    ) -> pd.DataFrame:
        """
        Calculate Bollinger Bands.

        Args:
            df: DataFrame with stock data.
            period: Lookback period.
            std_dev: Number of standard deviations.
            column: Column to use.

        Returns:
            DataFrame with Bollinger Bands columns.
        """
        if df is None or df.empty:
            logger.warning("Empty DataFrame passed to calculate_bollinger_bands")
            return df

        result = df.copy()
        sma = result[column].rolling(window=period).mean()
        rolling_std = result[column].rolling(window=period).std()

        result["BB_Upper"] = sma + (rolling_std * std_dev)
        result["BB_Middle"] = sma
        result["BB_Lower"] = sma - (rolling_std * std_dev)

        logger.info(f"Bollinger Bands calculated (period={period}, std={std_dev})")
        return result

    @staticmethod
    def calculate_daily_returns(
        df: pd.DataFrame, column: str = "Close"
    ) -> pd.DataFrame:
        """
        Calculate daily percentage returns.

        Args:
            df: DataFrame with stock data.
            column: Column to calculate returns on.

        Returns:
            DataFrame with added Daily_Return column.
        """
        if df is None or df.empty:
            logger.warning("Empty DataFrame passed to calculate_daily_returns")
            return df

        result = df.copy()
        result["Daily_Return"] = result[column].pct_change() * 100

        logger.info("Daily returns calculated")
        return result

    @staticmethod
    def calculate_volume_ma(
        df: pd.DataFrame, period: int = 20
    ) -> pd.DataFrame:
        """
        Calculate Volume Moving Average.

        Args:
            df: DataFrame with stock data.
            period: Moving average period.

        Returns:
            DataFrame with added Volume_MA column.
        """
        if df is None or df.empty:
            logger.warning("Empty DataFrame passed to calculate_volume_ma")
            return df

        result = df.copy()
        result["Volume_MA"] = result["Volume"].rolling(window=period).mean()

        logger.info(f"Volume MA calculated with period={period}")
        return result

    @staticmethod
    def get_summary_statistics(df: pd.DataFrame) -> dict:
        """
        Calculate summary statistics for stock data.

        Args:
            df: DataFrame with stock data.

        Returns:
            Dictionary with summary statistics.
        """
        if df is None or df.empty:
            return {}

        latest = df.iloc[-1]
        first = df.iloc[0]

        stats = {
            "latest_close": round(latest["Close"], 2),
            "latest_open": round(latest["Open"], 2),
            "latest_high": round(latest["High"], 2),
            "latest_low": round(latest["Low"], 2),
            "latest_volume": int(latest["Volume"]),
            "period_high": round(df["High"].max(), 2),
            "period_low": round(df["Low"].min(), 2),
            "avg_volume": int(df["Volume"].mean()),
            "total_records": len(df),
            "date_range_start": str(df.index.min().date()),
            "date_range_end": str(df.index.max().date()),
            "price_change": round(latest["Close"] - first["Close"], 2),
            "price_change_pct": round(
                ((latest["Close"] - first["Close"]) / first["Close"]) * 100, 2
            ),
        }

        logger.info("Summary statistics calculated")
        return stats
