"""
JOBPILOT — Structured Logging Setup

Uses Loguru for beautiful, structured logging.
Import: from utils.logger import logger
"""

import sys
from loguru import logger as _loguru_logger

# Remove default handler
_loguru_logger.remove()

# Console handler: colorful, human-readable output
_loguru_logger.add(
    sys.stdout,
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    ),
    level="DEBUG",
    colorize=True,
)

# File handler: persisted logs, rotated at 10MB, kept for 7 days
_loguru_logger.add(
    "logs/jobpilot_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
    rotation="10 MB",
    retention="7 days",
    compression="zip",
    level="DEBUG",
)

# Export configured logger instance
logger = _loguru_logger
