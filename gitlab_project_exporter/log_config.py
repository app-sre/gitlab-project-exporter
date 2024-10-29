import logging
import logging.config

from .config import Settings


def set_logging(settings: Settings) -> None:
    logging_config = {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {
            "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
        },
        "handlers": {
            "default": {
                "level": "INFO",
                "formatter": "standard",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",  # Default is stderr
            },
        },
        "loggers": {
            "": {  # root logger
                "level": settings.log_level,
                "handlers": ["default"],
                "propagate": False,
            },
            "uvicorn.error": {
                "level": settings.log_level,
                "handlers": ["default"],
            },
            "uvicorn.access": {
                "level": settings.log_level,
                "handlers": ["default"],
            },
        },
    }

    logging.config.dictConfig(logging_config)
    logging.getLogger("uvicorn").handlers.clear()  # to avoid duplicates
