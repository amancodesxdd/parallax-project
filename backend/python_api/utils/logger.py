import logging
import os
from logging.handlers import RotatingFileHandler


LOG_DIR = "logs"
LOG_FILE = os.path.join(
    LOG_DIR,
    "parallax.log"
)


def setup_logging():
    """
    Configure application-wide logging.

    Logs are written both to:
    1. Console
    2. Rotating log file
    """

    os.makedirs(
        LOG_DIR,
        exist_ok=True
    )

    formatter = logging.Formatter(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(message)s"
    )

    # ---------------------------------------------
    # Console handler
    # ---------------------------------------------

    console_handler = logging.StreamHandler()

    console_handler.setFormatter(
        formatter
    )

    # ---------------------------------------------
    # File handler
    # ---------------------------------------------

    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8"
    )

    file_handler.setFormatter(
        formatter
    )

    # ---------------------------------------------
    # Root logger
    # ---------------------------------------------

    root_logger = logging.getLogger()

    root_logger.setLevel(
        logging.INFO
    )

    # Prevent duplicate handlers
    if not root_logger.handlers:

        root_logger.addHandler(
            console_handler
        )

        root_logger.addHandler(
            file_handler
        )