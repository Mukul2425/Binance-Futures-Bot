import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def configure_logging(log_file: str | None = None, level: int = logging.INFO) -> None:
    """
    Configure application-wide logging.

    - Logs to both console and a rotating file in the `logs/` directory.
    - Keeps log format consistent across the app.
    """
    logs_dir = Path(__file__).resolve().parent.parent / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    if log_file is None:
        log_file = str(logs_dir / "trading_bot.log")
    else:
        log_file = str(logs_dir / log_file)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    root_logger = logging.getLogger()
    # Avoid adding duplicate handlers if configure_logging is called multiple times
    if root_logger.handlers:
        return

    root_logger.setLevel(level)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler (rotating)
    file_handler = RotatingFileHandler(
        log_file, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

