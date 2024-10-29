from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    gitlab_url: str = "https://gitlab.com"
    gitlab_token: str = ""
    project_ids: list[str]
    gitlab_ssl_verify: bool = True
    log_level: str = "INFO"
