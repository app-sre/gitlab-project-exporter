from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    gitlab_url: str = "https://gitlab.com"
    gitlab_token: str = ""
    gitlab_ssl_verify: bool = True
    log_level: str = "INFO"
    max_collector_threadpool_workers: int = 10  # Gitlab Client default session pool
    project_ids: list[str]
    uvicorn_host: str = "127.0.0.1"
    uvicorn_port: int = 8080
    uvicorn_reload: bool = False
