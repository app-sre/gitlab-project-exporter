import os
from collections.abc import Iterable
from http import HTTPStatus
from shutil import rmtree
from tempfile import mkdtemp

import pytest
import responses
from gitlab import Gitlab

from gitlab_project_exporter.gitlab_project import (
    GitlabProject,
    MirrorStatusCode,
    RemoteMirrorStatus,
)

GITLAB_URL = "https://gitlab.mine"
PROJECT_ID = 107187
PROJECT_URL = f"{GITLAB_URL}/api/v4/projects/{PROJECT_ID}"
REMOTE_MIRROR_STATUS_OK = RemoteMirrorStatus(
    mirror_id="1", url="http://good-mirror.org", status=MirrorStatusCode.OK
)
REMOTE_MIRROR_STATUS_KO = RemoteMirrorStatus(
    mirror_id="2", url="http://bad-mirror.org", status=MirrorStatusCode.KO
)


os.environ["PROJECT_IDS"] = f'["{PROJECT_ID}"]'
os.environ["GITLAB_URL"] = GITLAB_URL
os.environ["PROMETHEUS_MULTIPROC_DIR"] = mkdtemp()


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:  # noqa: ARG001
    rmtree(os.environ["PROMETHEUS_MULTIPROC_DIR"])


@pytest.fixture
def project() -> Iterable[GitlabProject]:
    project_content = {"name": "rporresm/mirror-test", "id": PROJECT_ID}
    with responses.RequestsMock() as rsps:
        rsps.add(
            method=responses.GET,
            url=PROJECT_URL,
            json=project_content,
            content_type="application/json",
            status=HTTPStatus.OK,
        )

        yield GitlabProject(
            gitlab_client=Gitlab(GITLAB_URL), project_id=str(PROJECT_ID)
        )
