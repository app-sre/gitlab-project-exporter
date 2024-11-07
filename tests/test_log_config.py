import pytest

from gitlab_project_exporter.config import Settings
from gitlab_project_exporter.log_config import get_log_config


@pytest.mark.parametrize("log_level", ["DEBUG", "INFO"])
def test_log_config_debug(log_level: str) -> None:
    settings = Settings(project_ids=["1234"], log_level=log_level)
    log_config = get_log_config(settings)
    assert log_config["loggers"][""]["level"] == log_level
    assert log_config["loggers"]["uvicorn"]["level"] == log_level
    assert log_config["loggers"]["uvicorn.error"]["level"] == log_level
    assert log_config["loggers"]["uvicorn.access"]["level"] == log_level
