from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture

from gitlab_project_exporter.gitlab_project import GitlabProject
from gitlab_project_exporter.main import app

from .conftest import REMOTE_MIRROR_STATUS_KO, REMOTE_MIRROR_STATUS_OK

client = TestClient(app, raise_server_exceptions=False)


def test_healthz() -> None:
    response = client.get("/healthz")
    assert response.status_code == HTTPStatus.OK


@pytest.mark.usefixtures("project")
def test_metrics(mocker: MockerFixture) -> None:
    project_mocker = mocker.patch.object(GitlabProject, "get_remote_mirrors_status")
    project_mocker.return_value = [REMOTE_MIRROR_STATUS_OK, REMOTE_MIRROR_STATUS_KO]

    response = client.get("/metrics/")
    assert response.status_code == HTTPStatus.OK
    assert "gitlab_remote_mirror_status" in response.text


@pytest.mark.usefixtures("project")
def test_metrics_ko(mocker: MockerFixture) -> None:
    project_mocker = mocker.patch.object(GitlabProject, "get_remote_mirrors_status")
    project_mocker.side_effect = ConnectionError()

    response = client.get("/metrics/")
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
