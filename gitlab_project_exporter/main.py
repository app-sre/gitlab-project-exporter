import uvicorn

from gitlab_project_exporter.config import Settings
from gitlab_project_exporter.log_config import get_log_config
from gitlab_project_exporter.server import create_app

app = create_app()
if __name__ == "__main__":
    settings = Settings()  # type: ignore[call-arg]
    log_config = get_log_config(settings)
    args = {
        "log_config": log_config,
        "host": settings.uvicorn_host,
        "port": settings.uvicorn_port,
    }

    if settings.uvicorn_reload:
        args |= {"reload": True}

    uvicorn.run("gitlab_project_exporter.main:app", **args)  # type: ignore[arg-type]
