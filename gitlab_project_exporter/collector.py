import logging
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from http import HTTPStatus

from gitlab import Gitlab
from gitlab.exceptions import GitlabGetError
from prometheus_client.core import GaugeMetricFamily, Metric
from prometheus_client.registry import Collector

from .gitlab_project import (
    GetRemoteMirrorsStatusType,
    GitlabProject,
)

LOG = logging.getLogger(__name__)


# Using python's dataclass as pydantic doesn't like exception types
@dataclass
class RemoteMirrorCollectionResult:
    project_id: str
    status: GetRemoteMirrorsStatusType | None = None
    exception: Exception | None = None

    def __post_init__(self) -> None:
        """Status and exception cannot defined at the same time or not defined."""
        if not bool(self.status) ^ bool(self.exception):
            msg = "You have to set either status or exception."
            raise ValueError(msg)


class GitLabProjectCollector(Collector):
    def __init__(self, gitlab_client: Gitlab, project_ids: Iterable[str]) -> None:
        super().__init__()
        self.gl = gitlab_client
        self.project_ids = project_ids

    def collect(self) -> Iterable[Metric]:
        yield self.collect_all_projects_remote_mirrors()

    def collect_all_projects_remote_mirrors(self) -> GaugeMetricFamily:
        gauge = GaugeMetricFamily(
            "gitlab_remote_mirror_status",
            "GitLab Remote Mirror status",
            labels=["project_id", "mirror_id", "mirror_url"],
        )

        with ThreadPoolExecutor() as executor:
            for result in executor.map(
                self.collect_project_remote_mirrors, self.project_ids
            ):
                if result.exception:
                    if (
                        isinstance(result.exception, GitlabGetError)
                        and result.exception.response_code == HTTPStatus.NOT_FOUND
                    ):
                        LOG.error("Project %s does not exist.", result.project_id)
                    else:
                        LOG.error(
                            "Error collecting project %s: %s",
                            result.project_id,
                            result.exception,
                        )
                        raise result.exception
                else:
                    for mirror_status in result.status or []:
                        gauge.add_metric(
                            [
                                result.project_id,
                                mirror_status.mirror_id,
                                mirror_status.url,
                            ],
                            mirror_status.status,
                        )

        return gauge

    def collect_project_remote_mirrors(
        self, project_id: str
    ) -> RemoteMirrorCollectionResult:
        try:
            project = GitlabProject(gitlab_client=self.gl, project_id=project_id)
            result = RemoteMirrorCollectionResult(
                project_id=project_id, status=project.get_remote_mirrors_status()
            )

        # ThreadPoolExecutor catches and ignores all exceptions, hence the wide catch
        # here. It will be analyzed and acted upon above.
        except Exception as e:  # noqa: BLE001
            result = RemoteMirrorCollectionResult(project_id=project_id, exception=e)

        return result
