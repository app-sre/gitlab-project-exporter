import logging
from collections.abc import Callable

from fastapi import FastAPI
from gitlab import Gitlab
from prometheus_client import CollectorRegistry, make_asgi_app, multiprocess

from .collector import GitLabProjectCollector
from .config import settings

LOG = logging.getLogger(__name__)
LOG.info("Starting gitlab-projects-exporter")


def make_metrics_app() -> Callable:
    registry = CollectorRegistry()
    gl = Gitlab(
        settings.gitlab_url,
        private_token=settings.gitlab_token,
        ssl_verify=settings.gitlab_ssl_verify,
    )
    registry.register(
        GitLabProjectCollector(gitlab_client=gl, project_ids=settings.project_ids)
    )
    multiprocess.MultiProcessCollector(registry)
    return make_asgi_app(registry=registry)


app = FastAPI(
    title="Gitlab Projects Prometheus Exporter",
    description="Prometheus exporter for GitLab Projects API",
    version="0.1.0",
    openapi_url=None,
    redoc_url=None,
    docs_url=None,
)


metrics_app = make_metrics_app()
app.mount("/metrics", metrics_app)


@app.get("/healthz", include_in_schema=False)
async def healthz() -> str:
    return "ok"
