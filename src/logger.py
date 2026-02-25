"""Logging configuration."""

import logging
import os
from datetime import datetime

from config import LOGS_DIR


def setup_logger(name: str = "stock_dashboard") -> logging.Logger:
    """Initialize and return a logger."""
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # File handler - logs everything to a daily log file
    log_filename = f"dashboard_{datetime.now().strftime('%Y-%m-%d')}.log"
    log_filepath = os.path.join(LOGS_DIR, log_filename)

    file_handler = logging.FileHandler(log_filepath, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)

    # Console handler - logs INFO and above
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Formatters
    detailed_formatter = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    simple_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%H:%M:%S",
    )

    file_handler.setFormatter(detailed_formatter)
    console_handler.setFormatter(simple_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info("Logger initialized successfully.")
    return logger


# Module-level logger instance
logger = setup_logger()
