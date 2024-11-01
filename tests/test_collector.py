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
from gitlab_project_exporter.gitlab_project import (
    GitlabProject,
    RemoteMirrorStatus,
)

MAX_WORKERS = 10


@pytest.fixture
def collector(gitlab_url: str, project_id: int) -> GitLabProjectCollector:
    return GitLabProjectCollector(
        gitlab_client=Gitlab(gitlab_url),
        project_ids=[str(project_id)],
        max_workers=MAX_WORKERS,
    )


@pytest.mark.usefixtures("project")
def test_collect_remote_mirror(
    collector: GitLabProjectCollector,
    mocker: MockerFixture,
    project_id: int,
    remote_mirror_status_ok: RemoteMirrorStatus,
    remote_mirror_status_ko: RemoteMirrorStatus,
) -> None:
    project_mocker = mocker.patch.object(GitlabProject, "get_remote_mirrors_status")
    project_mocker.return_value = [remote_mirror_status_ok, remote_mirror_status_ko]
    assert collector.collect_project_remote_mirrors(
        str(project_id)
    ) == RemoteMirrorCollectionResult(
        project_id=str(project_id),
        status=[remote_mirror_status_ok, remote_mirror_status_ko],
    )


@pytest.mark.usefixtures("project")
def test_collect_remote_mirror_exception(
    collector: GitLabProjectCollector,
    mocker: MockerFixture,
    project_id: int,
) -> None:
    project_mocker = mocker.patch.object(GitlabProject, "get_remote_mirrors_status")
    exception = ConnectionError()
    project_mocker.side_effect = exception
    assert collector.collect_project_remote_mirrors(
        str(project_id)
    ) == RemoteMirrorCollectionResult(project_id=str(project_id), exception=exception)


@pytest.mark.usefixtures("project")
def test_collector(
    collector: GitLabProjectCollector,
    mocker: MockerFixture,
    project_id: int,
    remote_mirror_status_ok: RemoteMirrorStatus,
    remote_mirror_status_ko: RemoteMirrorStatus,
) -> None:
    project_mocker = mocker.patch.object(GitlabProject, "get_remote_mirrors_status")
    project_mocker.return_value = [remote_mirror_status_ok, remote_mirror_status_ko]

    expected_metric = GaugeMetricFamily(
        "gitlab_remote_mirror_status",
        "GitLab Remote Mirror status",
        labels=["project_id", "mirror_id", "mirror_url"],
    )
    expected_metric.add_metric(
        [
            str(project_id),
            remote_mirror_status_ok.mirror_id,
            remote_mirror_status_ok.url,
        ],
        remote_mirror_status_ok.status,
    )
    expected_metric.add_metric(
        [
            str(project_id),
            remote_mirror_status_ko.mirror_id,
            remote_mirror_status_ko.url,
        ],
        remote_mirror_status_ko.status,
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
