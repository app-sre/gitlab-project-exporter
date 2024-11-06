from gitlab_project_exporter.config import Settings


# based on uvicorn.logging.LOGGING_CONFIG
# it adds a default logger and unified log level
def get_log_config(settings: Settings) -> dict:
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": "uvicorn.logging.DefaultFormatter",
                "fmt": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            },
            "access": {
                "()": "uvicorn.logging.AccessFormatter",
                "fmt": "%(asctime)s [%(levelname)s] %(client_addr)s - %(request_line)s %(status_code)s",
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
            },
            "access": {
                "formatter": "access",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "": {  # root logger
                "level": settings.log_level,
                "handlers": ["default"],
                "propagate": False,
            },
            "uvicorn": {
                "handlers": ["default"],
                "level": settings.log_level,
                "propagate": False,
            },
            "uvicorn.error": {"level": settings.log_level},
            "uvicorn.access": {
                "handlers": ["access"],
                "level": settings.log_level,
                "propagate": False,
            },
        },
    }
