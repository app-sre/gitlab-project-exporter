from http import HTTPStatus
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture

from gitlab_project_exporter.gitlab_project import (
    GitlabProject,
    RemoteMirrorStatus,
)
from gitlab_project_exporter.server import create_app


@pytest.fixture(autouse=True)
def patch_env(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, project_id: int, gitlab_url: str
) -> None:
    monkeypatch.setenv("PROJECT_IDS", f'["{project_id}"]')
    monkeypatch.setenv("GITLAB_URL", gitlab_url)
    monkeypatch.setenv("PROMETHEUS_MULTIPROC_DIR", str(tmp_path))


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app(), raise_server_exceptions=False)


def test_healthz(client: TestClient) -> None:
    response = client.get("/healthz")
    assert response.status_code == HTTPStatus.OK


@pytest.mark.usefixtures("project")
def test_metrics(
    mocker: MockerFixture,
    remote_mirror_status_ok: RemoteMirrorStatus,
    remote_mirror_status_failed: RemoteMirrorStatus,
    client: TestClient,
) -> None:
    project_mocker = mocker.patch.object(GitlabProject, "get_remote_mirrors_status")
    project_mocker.return_value = [remote_mirror_status_ok, remote_mirror_status_failed]

    response = client.get("/metrics/")
    assert response.status_code == HTTPStatus.OK
    assert "gitlab_remote_mirror_status" in response.text


@pytest.mark.usefixtures("project")
def test_metrics_failed(mocker: MockerFixture, client: TestClient) -> None:
    project_mocker = mocker.patch.object(GitlabProject, "get_remote_mirrors_status")
    project_mocker.side_effect = ConnectionError()

    response = client.get("/metrics/")
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
