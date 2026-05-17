"""Logging utilities with OTEL instrumentation."""

import logging
import logging.config
import json
from datetime import datetime
import sys
from app.config import settings


def setup_logging():
    """Setup structured JSON logging."""
    
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": "%(asctime)s %(name)s %(levelname)s %(message)s"
            },
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": settings.log_level,
                "formatter": "standard",
                "stream": "ext://sys.stdout"
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": settings.log_level,
                "formatter": "json",
                "filename": "logs/app.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5
            }
        },
        "root": {
            "level": settings.log_level,
            "handlers": ["console", "file"]
        }
    }
    
    try:
        logging.config.dictConfig(logging_config)
    except Exception as e:
        # Fallback if pythonjsonlogger is not available
        logging.basicConfig(
            level=settings.log_level,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )
        logging.warning(f"Could not setup JSON logging: {e}")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)
