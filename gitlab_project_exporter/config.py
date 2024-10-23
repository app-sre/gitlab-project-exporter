import logging
import logging.config

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    gitlab_url: str = "https://gitlab.com"
    gitlab_token: str = ""
    project_ids: list[str]
    gitlab_ssl_verify: bool = True
    log_level: str = "INFO"


# mypy complains about Missing named argument "project_ids
settings = Settings()  # type: ignore[call-arg]

LOGGING_CONFIG = {
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

logging.config.dictConfig(LOGGING_CONFIG)
logging.getLogger("uvicorn").handlers.clear()  # to avoid duplicates
