import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, Optional

from api_monitoring.config import settings


class StructuredLogFormatter(logging.Formatter):
    """Custom formatter for structured JSON logs."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if available
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields if available
        for key, value in record.__dict__.items():
            if key not in log_data and not key.startswith('_') and key != 'exc_info':
                log_data[key] = value

        return json.dumps(log_data)


def get_logger(name: str, extra: Optional[Dict[str, Any]] = None) -> logging.Logger:
    """
    Get a logger with the specified name and extra fields.

    Args:
        name: The name of the logger
        extra: Extra fields to include in all log messages

    Returns:
        A configured logger instance
    """
    logger = logging.getLogger(name)

    # Only configure if not already configured
    if not logger.handlers:
        # Set log level from settings
        log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
        logger.setLevel(log_level)

        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(StructuredLogFormatter())
        logger.addHandler(console_handler)

        # Create file handler if log file is specified
        if settings.log_file:
            file_handler = logging.FileHandler(settings.log_file)
            file_handler.setFormatter(StructuredLogFormatter())
            logger.addHandler(file_handler)

    # Create a filter to add extra fields
    if extra:
        class ExtraFilter(logging.Filter):
            def filter(self, record):
                for key, value in extra.items():
                    setattr(record, key, value)
                return True

        extra_filter = ExtraFilter()
        logger.addFilter(extra_filter)

    return logger


# Create a default logger for the application
logger = get_logger("api_monitoring")
