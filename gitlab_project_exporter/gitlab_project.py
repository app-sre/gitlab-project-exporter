import logging
from enum import IntEnum
from typing import Never

from gitlab import Gitlab
from pydantic import BaseModel

LOG = logging.getLogger(__name__)
TIMEOUT = 10


class MirrorStatusCode(IntEnum):
    OK = 0
    KO = 1


class RemoteMirrorStatus(BaseModel):
    mirror_id: str
    url: str
    status: MirrorStatusCode


GetRemoteMirrorsStatusType = list[RemoteMirrorStatus] | list[Never]


class GitlabProject:
    def __init__(
        self, project_id: str, gitlab_client: Gitlab, timeout: int = TIMEOUT
    ) -> None:
        self.timeout = timeout
        self.project = gitlab_client.projects.get(project_id, timeout=self.timeout)

    def get_remote_mirrors_status(self) -> GetRemoteMirrorsStatusType:
        mirrors = self.project.remote_mirrors.list(timeout=self.timeout)
        response = []
        for m in mirrors:
            status = (
                MirrorStatusCode.KO
                if m.last_update_started_at > m.last_successful_update_at
                else MirrorStatusCode.OK
            )
            response.append(
                RemoteMirrorStatus(mirror_id=str(m.id), url=m.url, status=status)
            )

        return response
