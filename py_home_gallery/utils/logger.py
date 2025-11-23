"""
Logging utilities for Py Home Gallery.

This module provides centralized logging configuration and utilities
for consistent logging across the application.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


# Default log format
DEFAULT_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


def setup_logger(
    name: str = 'py_home_gallery',
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    console: bool = True
) -> logging.Logger:
    """
    Set up and configure a logger for the application.
    
    Args:
        name: Name of the logger
        level: Logging level (default: INFO)
        log_file: Optional path to log file
        console: Whether to also log to console (default: True)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(DEFAULT_FORMAT, DATE_FORMAT)
    
    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        # Create log directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = 'py_home_gallery') -> logging.Logger:
    """
    Get an existing logger or create a new one with configured settings.

    Args:
        name: Name of the logger

    Returns:
        logging.Logger: Logger instance
    """
    logger = logging.getLogger(name)

    # Only configure handlers for the root logger
    # Child loggers will propagate to parent (no duplicate handlers)
    if name == 'py_home_gallery' and not logger.handlers:
        log_file = f"{_log_dir}/app.log" if _log_to_file else None
        setup_logger(name, level=_log_level, log_file=log_file, console=True)

    # Child loggers just inherit from parent
    logger.setLevel(_log_level)

    return logger


# Global logger configuration
_log_level = logging.INFO
_log_to_file = True
_log_dir = './logs'


def configure_logging(log_level: str = 'INFO', log_to_file: bool = True, log_dir: str = './logs') -> None:
    """
    Configure global logging settings.
    
    Should be called once during application startup with config values.
    
    Args:
        log_level: Log level string ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        log_to_file: Whether to log to file
        log_dir: Directory for log files
    """
    global _log_level, _log_to_file, _log_dir
    
    # Convert string level to logging constant
    level_map = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    _log_level = level_map.get(log_level.upper(), logging.INFO)
    _log_to_file = log_to_file
    _log_dir = log_dir
    
    # Recreate root logger with new settings
    log_file = f"{_log_dir}/app.log" if _log_to_file else None
    setup_logger('py_home_gallery', level=_log_level, log_file=log_file, console=True)
    
    logger = logging.getLogger('py_home_gallery')
    logger.info(f"Logging configured - Level: {log_level}, File: {log_to_file}, Dir: {log_dir}")


# Module-level logger instance
logger = get_logger()

