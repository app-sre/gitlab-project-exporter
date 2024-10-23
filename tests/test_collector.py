from http import HTTPStatus

import pytest
from gitlab import Gitlab
from gitlab.exceptions import GitlabGetError
from prometheus_client.core import GaugeMetricFamily
from pytest_mock import MockerFixture

from gitlab_project_exporter.collector import (
    GitLabProjectCollector,
    RemoteMirrorCollectionResult,
)
from gitlab_project_exporter.gitlab_project import GitlabProject

from .conftest import (
    GITLAB_URL,
    PROJECT_ID,
    REMOTE_MIRROR_STATUS_KO,
    REMOTE_MIRROR_STATUS_OK,
)


@pytest.fixture
def collector() -> GitLabProjectCollector:
    return GitLabProjectCollector(
        gitlab_client=Gitlab(GITLAB_URL), project_ids=[str(PROJECT_ID)]
    )


@pytest.mark.usefixtures("project")
def test_collect_remote_mirror(
    collector: GitLabProjectCollector, mocker: MockerFixture
) -> None:
    project_mocker = mocker.patch.object(GitlabProject, "get_remote_mirrors_status")
    project_mocker.return_value = [REMOTE_MIRROR_STATUS_OK, REMOTE_MIRROR_STATUS_KO]
    assert collector.collect_project_remote_mirrors(
        str(PROJECT_ID)
    ) == RemoteMirrorCollectionResult(
        project_id=str(PROJECT_ID),
        status=[REMOTE_MIRROR_STATUS_OK, REMOTE_MIRROR_STATUS_KO],
    )


@pytest.mark.usefixtures("project")
def test_collect_remote_mirror_exception(
    collector: GitLabProjectCollector, mocker: MockerFixture
) -> None:
    project_mocker = mocker.patch.object(GitlabProject, "get_remote_mirrors_status")
    exception = ConnectionError()
    project_mocker.side_effect = exception
    assert collector.collect_project_remote_mirrors(
        str(PROJECT_ID)
    ) == RemoteMirrorCollectionResult(project_id=str(PROJECT_ID), exception=exception)


@pytest.mark.usefixtures("project")
def test_collector(collector: GitLabProjectCollector, mocker: MockerFixture) -> None:
    project_mocker = mocker.patch.object(GitlabProject, "get_remote_mirrors_status")
    project_mocker.return_value = [REMOTE_MIRROR_STATUS_OK, REMOTE_MIRROR_STATUS_KO]

    expected_metric = GaugeMetricFamily(
        "gitlab_remote_mirror_status",
        "GitLab Remote Mirror status",
        labels=["project_id", "mirror_id", "mirror_url"],
    )
    expected_metric.add_metric(
        [
            str(PROJECT_ID),
            REMOTE_MIRROR_STATUS_OK.mirror_id,
            REMOTE_MIRROR_STATUS_OK.url,
        ],
        REMOTE_MIRROR_STATUS_OK.status,
    )
    expected_metric.add_metric(
        [
            str(PROJECT_ID),
            REMOTE_MIRROR_STATUS_KO.mirror_id,
            REMOTE_MIRROR_STATUS_KO.url,
        ],
        REMOTE_MIRROR_STATUS_KO.status,
    )

    assert collector.collect_all_projects_remote_mirrors() == expected_metric


@pytest.mark.usefixtures("project")
def test_collector_generic_exception(
    collector: GitLabProjectCollector, mocker: MockerFixture
) -> None:
    project_mocker = mocker.patch.object(GitlabProject, "get_remote_mirrors_status")
    project_mocker.side_effect = ConnectionError()
    with pytest.raises(ConnectionError):
        collector.collect_all_projects_remote_mirrors()


@pytest.mark.usefixtures("project")
def test_collector_gitlab_get_error_exception(
    collector: GitLabProjectCollector, mocker: MockerFixture
) -> None:
    project_mocker = mocker.patch.object(GitlabProject, "get_remote_mirrors_status")
    project_mocker.side_effect = GitlabGetError(
        error_message="error", response_code=HTTPStatus.NOT_FOUND
    )
    expected_metric = GaugeMetricFamily(
        "gitlab_remote_mirror_status",
        "GitLab Remote Mirror status",
        labels=["project_id", "mirror_id", "mirror_url"],
    )
    assert collector.collect_all_projects_remote_mirrors() == expected_metric
