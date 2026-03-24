"""
╔═══════════════════════════════════════════════════════════════════╗
║  JOBPILOT — Structured Logging                                   ║
║                                                                   ║
║  Uses Loguru for structured, colorful, filterable logging.        ║
║  All modules should import logger from here:                      ║
║                                                                   ║
║    from utils.logger import logger                                ║
║    logger.info("Scraping LinkedIn...")                            ║
║    logger.error("Failed to connect", exc_info=True)              ║
║                                                                   ║
║  LOG LEVELS:                                                      ║
║    DEBUG   → Detailed diagnostic info (scraper selectors, etc.)  ║
║    INFO    → General operational events (job found, applied)     ║
║    WARNING → Something unexpected but recoverable                ║
║    ERROR   → Something failed (scrape failed, API error)         ║
║    CRITICAL → App cannot continue                                ║
╚═══════════════════════════════════════════════════════════════════╝
"""

import sys
from loguru import logger as _loguru_logger

# Remove default handler (Loguru adds one automatically)
_loguru_logger.remove()

# ─────────────────────────────────────
# Console handler — colorful, human-readable
# ─────────────────────────────────────
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

# ─────────────────────────────────────
# File handler — JSON-structured for analysis
# Logs rotate at 10MB, kept for 7 days
# ─────────────────────────────────────
_loguru_logger.add(
    "logs/jobpilot_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
    rotation="10 MB",       # New file every 10MB
    retention="7 days",     # Delete old logs after 7 days
    compression="zip",      # Compress rotated logs
    level="DEBUG",
)

# ─────────────────────────────────────
# Export the configured logger
# ─────────────────────────────────────
logger = _loguru_logger
