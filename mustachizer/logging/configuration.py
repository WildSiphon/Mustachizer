import logging.config

from mustachizer.logging import LOGGING_LEVEL_LIST
from mustachizer.logging.errors import LoggingLevelError

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "file": {
            "format": "%(asctime)s - %(filename)s - %(levelname)s - %(message)s",
        },
        "console": {
            "format": "%(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",  # Default is stderr
            "formatter": "console",
            "level": None,  # Defined in ConfigureLogger
        },
    },
    "loggers": {
        "stachlog": {
            "handlers": ["console"],
            "propagate": False,
            "level": "DEBUG",  # Should be lower than handlers levels
        }
    },
}


def ConfigureLogger(log_file: str = "", console_level: str = "INFO") -> None:
    """
    Use LOGGING_CONFIG as configuration for logger.

    :param logger_type: if set, log in a file too. By default log only in console
    :param console_level: choose console log level
    """

    # Check log level
    level = console_level.upper()
    if level not in LOGGING_LEVEL_LIST:
        error = (
            f"'{level}' is not a correct level for logging. "
            f"Log level must be in {LOGGING_LEVEL_LIST}."
        )
        raise LoggingLevelError(error)

    # Manually set console log level
    LOGGING_CONFIG["handlers"]["console"]["level"] = level

    # If logger_name is set
    if log_file:
        LOGGING_CONFIG["loggers"]["stachlog"]["handlers"].append("file")
        LOGGING_CONFIG["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": f"{log_file}.log",
            "mode": "a",
            "formatter": "file",
            "level": "DEBUG",
            "maxBytes": 512000,
            "backupCount": 10,
        }

    # Configure logging
    logging.config.dictConfig(LOGGING_CONFIG)
