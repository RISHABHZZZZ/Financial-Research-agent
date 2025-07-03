# app/logging_config.py

import logging
import sys

def setup_logger(name: str) -> logging.Logger:
    """
    Sets up and returns a logger with DEBUG level and console output.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Avoid duplicate handlers if re-imported
    if not logger.handlers:
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # Optional: File handler (uncomment if you want log files)
        # file_handler = logging.FileHandler("app.log")
        # file_handler.setLevel(logging.DEBUG)
        # file_handler.setFormatter(console_formatter)
        # logger.addHandler(file_handler)

    return logger
