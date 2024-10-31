from http import HTTPStatus

import responses

from gitlab_project_exporter.gitlab_project import (
    GitlabProject,
    MirrorStatusCode,
    RemoteMirrorStatus,
)


def test_init_project_object(project: GitlabProject) -> None:
    assert project.project.name


def test_remote_mirrors_ok(project: GitlabProject, project_url: str) -> None:
    mirror_response = {
        "id": 1210,
        "enabled": True,
        "url": "https://*****:*****@github.com/rporres/mirror-test-from-gitlab.git",
        "update_status": "finished",
        "last_update_at": "2024-10-22T11:43:58.814Z",
        "last_update_started_at": "2024-10-22T11:43:57.518Z",
        "last_successful_update_at": "2024-10-22T11:43:58.814Z",
        "last_error": None,
        "only_protected_branches": True,
        "keep_divergent_refs": False,
        "auth_method": "password",
        "mirror_branch_regex": None,
    }
    with responses.RequestsMock() as rsps:
        rsps.add(
            method=responses.GET,
            url=f"{project_url}/remote_mirrors",
            json=[mirror_response],
            content_type="application/json",
            status=HTTPStatus.OK,
        )

        mirrors = project.get_remote_mirrors_status()
        assert mirrors == [
            RemoteMirrorStatus(
                mirror_id=str(mirror_response["id"]),
                status=MirrorStatusCode.OK,
                url=str(mirror_response["url"]),
            )
        ]


# No parametrized fixtures :(
# See https://github.com/pytest-dev/pytest/issues/349


def test_remote_mirrors_to_retry_ko(project: GitlabProject, project_url: str) -> None:
    mirror_response = {
        "id": 1210,
        "enabled": True,
        "url": "https://*****:*****@github.com/rporres/mirror-test-from-gitlab.git",
        "update_status": "to_retry",
        "last_update_at": "2024-10-22T11:25:10.041Z",
        "last_update_started_at": "2024-10-22T11:36:56.199Z",
        "last_successful_update_at": "2024-10-22T11:25:10.041Z",
        "last_error": "13:get remote references: create git ls-remote: exit status 128, stderr: \"remote: Write access to repository not granted.\\nfatal: unable to access 'https://github.com/rporres/mirror-test-from-gitlab.git/': The requested URL returned error: 403\\n\".",
        "only_protected_branches": True,
        "keep_divergent_refs": False,
        "auth_method": "password",
        "mirror_branch_regex": None,
    }
    with responses.RequestsMock() as rsps:
        rsps.add(
            method=responses.GET,
            url=f"{project_url}/remote_mirrors",
            json=[mirror_response],
            content_type="application/json",
            status=HTTPStatus.OK,
        )

        mirrors = project.get_remote_mirrors_status()
        assert mirrors == [
            RemoteMirrorStatus(
                mirror_id=str(mirror_response["id"]),
                status=MirrorStatusCode.KO,
                url=str(mirror_response["url"]),
            )
        ]


def test_remote_mirrors_failed_ko(project: GitlabProject, project_url: str) -> None:
    mirror_response = {
        "id": 1210,
        "enabled": True,
        "url": "https://*****:*****@github.com/rporres/mirror-test-from-gitlab.git",
        "update_status": "failed",
        "last_update_at": "2024-10-22T11:25:10.041Z",
        "last_update_started_at": "2024-10-22T11:36:56.199Z",
        "last_successful_update_at": "2024-10-22T11:25:10.041Z",
        "last_error": "13:get remote references: create git ls-remote: exit status 128, stderr: \"remote: Write access to repository not granted.\\nfatal: unable to access 'https://github.com/rporres/mirror-test-from-gitlab.git/': The requested URL returned error: 403\\n\".",
        "only_protected_branches": True,
        "keep_divergent_refs": False,
        "auth_method": "password",
        "mirror_branch_regex": None,
    }
    with responses.RequestsMock() as rsps:
        rsps.add(
            method=responses.GET,
            url=f"{project_url}/remote_mirrors",
            json=[mirror_response],
            content_type="application/json",
            status=HTTPStatus.OK,
        )

        mirrors = project.get_remote_mirrors_status()
        assert mirrors == [
            RemoteMirrorStatus(
                mirror_id=str(mirror_response["id"]),
                status=MirrorStatusCode.KO,
                url=str(mirror_response["url"]),
            )
        ]


def test_remote_mirrors_none_ko(project: GitlabProject, project_url: str) -> None:
    mirror_response = {
        "id": 1213,
        "enabled": True,
        "url": "https://*****:*****@github.com/rporres/mirror-test-2",
        "update_status": "none",
        "last_update_at": None,
        "last_update_started_at": None,
        "last_successful_update_at": None,
        "last_error": None,
        "only_protected_branches": True,
        "keep_divergent_refs": False,
        "auth_method": "password",
        "mirror_branch_regex": None,
    }
    with responses.RequestsMock() as rsps:
        rsps.add(
            method=responses.GET,
            url=f"{project_url}/remote_mirrors",
            json=[mirror_response],
            content_type="application/json",
            status=HTTPStatus.OK,
        )

        mirrors = project.get_remote_mirrors_status()
        assert mirrors == [
            RemoteMirrorStatus(
                mirror_id=str(mirror_response["id"]),
                status=MirrorStatusCode.KO,
                url=str(mirror_response["url"]),
            )
        ]
