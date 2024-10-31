import logging
from enum import IntEnum
from typing import Never

from gitlab import Gitlab
from pydantic import BaseModel

LOG = logging.getLogger(__name__)
TIMEOUT = 10

# based on remote mirror state machine, see
# https://gitlab.com/gitlab-org/gitlab/-/blob/06cf7af7413c13c7cfd0a667e53014d0d0693280/app/models/remote_mirror.rb#L40-83
# Invluding none looks weird, but not having initialised the mirror can count as a
# failure as we would end up not having the mirror, which is what want at the end.
FAILURE_STATUS = {"to_retry", "failed", "none"}


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
                if m.update_status in FAILURE_STATUS
                else MirrorStatusCode.OK
            )
            response.append(
                RemoteMirrorStatus(mirror_id=str(m.id), url=m.url, status=status)
            )

        return response
