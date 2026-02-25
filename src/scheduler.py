"""
Scheduler module for auto-updating stock data.
Uses APScheduler for periodic data refresh.
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from src.data_fetcher import StockDataFetcher
from src.csv_handler import CSVHandler
from src.logger import logger
from config import AUTO_UPDATE_INTERVAL


class StockScheduler:
    """Manages scheduled updates for stock data."""

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.fetcher = StockDataFetcher()
        self.csv_handler = CSVHandler()
        self._watched_symbols = []
        self._is_running = False

    def add_stock(self, symbol: str):
        """Add a stock symbol to the watch list."""
        if symbol not in self._watched_symbols:
            self._watched_symbols.append(symbol)
            logger.info(f"Added {symbol} to scheduler watch list")

    def remove_stock(self, symbol: str):
        """Remove a stock symbol from the watch list."""
        if symbol in self._watched_symbols:
            self._watched_symbols.remove(symbol)
            logger.info(f"Removed {symbol} from scheduler watch list")

    def get_watched_symbols(self) -> list:
        """Return list of watched symbols."""
        return self._watched_symbols.copy()

    def _update_job(self):
        """Job that fetches and saves data for all watched symbols."""
        logger.info(
            f"Scheduler: Auto-updating {len(self._watched_symbols)} stocks..."
        )

        for symbol in self._watched_symbols:
            try:
                df = self.fetcher.fetch_daily_stock_data(symbol)
                if df is not None:
                    self.csv_handler.save_to_csv(df, symbol)
                    logger.info(f"Scheduler: Updated data for {symbol}")
                else:
                    logger.warning(f"Scheduler: No data returned for {symbol}")
            except Exception as e:
                logger.error(f"Scheduler: Error updating {symbol}: {e}")

        logger.info("Scheduler: Auto-update cycle complete")

    def start(self, interval_minutes: int = AUTO_UPDATE_INTERVAL):
        """
        Start the background scheduler.

        Args:
            interval_minutes: Update interval in minutes.
        """
        if self._is_running:
            logger.warning("Scheduler is already running")
            return

        if not self._watched_symbols:
            logger.warning("No stocks in watch list. Add stocks before starting.")
            return

        self.scheduler.add_job(
            self._update_job,
            trigger=IntervalTrigger(minutes=interval_minutes),
            id="stock_updater",
            name="Stock Data Auto-Updater",
            replace_existing=True,
        )
        self.scheduler.start()
        self._is_running = True
        logger.info(
            f"Scheduler started. Updating every {interval_minutes} minutes."
        )

    def stop(self):
        """Stop the background scheduler."""
        if self._is_running:
            self.scheduler.shutdown(wait=False)
            self._is_running = False
            logger.info("Scheduler stopped")
        else:
            logger.info("Scheduler was not running")

    @property
    def is_running(self) -> bool:
        """Check if scheduler is currently running."""
        return self._is_running
