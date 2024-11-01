from collections.abc import Callable

from fastapi import APIRouter, FastAPI
from gitlab import Gitlab
from prometheus_client import CollectorRegistry, make_asgi_app, multiprocess

from .collector import GitLabProjectCollector
from .config import Settings
from .log_config import set_logging

default_router = APIRouter()


@default_router.get("/healthz", include_in_schema=False)
def healthz() -> str:
    return "ok"


def make_metrics_app() -> Callable:
    # mypy complains about Missing named argument "project_ids"
    settings = Settings()  # type: ignore[call-arg]
    set_logging(settings)
    gl = Gitlab(
        settings.gitlab_url,
        private_token=settings.gitlab_token,
        ssl_verify=settings.gitlab_ssl_verify,
    )
    registry = CollectorRegistry()
    registry.register(
        GitLabProjectCollector(
            gitlab_client=gl,
            project_ids=settings.project_ids,
            max_workers=settings.max_collector_threadpool_workers,
        )
    )
    multiprocess.MultiProcessCollector(registry)
    return make_asgi_app(registry=registry)


def create_app() -> FastAPI:
    fast_api_app = FastAPI(
        title="Gitlab Projects Prometheus Exporter",
        description="Prometheus exporter for GitLab Projects API",
        version="0.1.0",
        openapi_url=None,
        redoc_url=None,
        docs_url=None,
    )
    fast_api_app.include_router(default_router)
    metrics_app = make_metrics_app()
    fast_api_app.mount("/metrics", metrics_app)

    return fast_api_app
