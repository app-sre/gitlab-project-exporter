from collections.abc import Iterable
from http import HTTPStatus

import pytest
import responses
from gitlab import Gitlab

from gitlab_project_exporter.gitlab_project import (
    GitlabProject,
    MirrorStatusCode,
    RemoteMirrorStatus,
)


@pytest.fixture
def gitlab_url() -> str:
    return "https://gitlab.mine"


@pytest.fixture
def project_id() -> int:
    return 107187


@pytest.fixture
def project_url(gitlab_url: str, project_id: str) -> str:
    return f"{gitlab_url}/api/v4/projects/{project_id}"


@pytest.fixture
def remote_mirror_status_ok() -> RemoteMirrorStatus:
    return RemoteMirrorStatus(
        mirror_id="1", url="http://good-mirror.org", status=MirrorStatusCode.OK
    )


@pytest.fixture
def remote_mirror_status_failed() -> RemoteMirrorStatus:
    return RemoteMirrorStatus(
        mirror_id="2", url="http://bad-mirror.org", status=MirrorStatusCode.FAILED
    )


@pytest.fixture
def project(
    project_id: int, project_url: str, gitlab_url: str
) -> Iterable[GitlabProject]:
    project_content = {"name": "rporresm/mirror-test", "id": project_id}
    with responses.RequestsMock() as rsps:
        rsps.add(
            method=responses.GET,
            url=project_url,
            json=project_content,
            content_type="application/json",
            status=HTTPStatus.OK,
        )

        yield GitlabProject(
            gitlab_client=Gitlab(gitlab_url), project_id=str(project_id)
        )
