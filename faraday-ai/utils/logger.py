"""
FARADAY AI - Logging System
Loguru-based logging with file and console output
"""

import sys
from pathlib import Path
from loguru import logger as _logger

# Remove default handler
_logger.remove()

# Add console handler with emoji formatting
_logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="INFO",
    colorize=True
)

# Note: File handler will be added in settings initialization to avoid circular imports


def setup_file_logging(log_file: Path, level: str = "INFO", rotation: str = "500 MB", retention: str = "10 days"):
    """
    Setup file logging.

    Args:
        log_file: Path to log file
        level: Log level
        rotation: When to rotate log file
        retention: How long to keep old logs
    """
    _logger.add(
        str(log_file),
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=level,
        rotation=rotation,
        retention=retention,
        encoding="utf-8"
    )
    _logger.info(f"📝 File logging enabled: {log_file}")


# Export logger
logger = _logger

__all__ = ['logger', 'setup_file_logging']
