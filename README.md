# gitlab-project-exporter

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Prometheus exporter for Gitlab projects using the [Uvicorn web server](https://www.uvicorn.org/)

## Metrics exported

| Metric name | Description |
|---|---|
| `gitlab_remote_mirror_status` | Gitlab [Remote Mirror]( https://docs.gitlab.com/ee/api/remote_mirrors.html ) status |

## Configuration

| Env variable | Mandatory | Default | Description |
|---|---|---|---|
| `PROJECT_IDS` | Yes |  | Gitlab Project IDS, e.g. '[ "user/project" ]' |
| `GITLAB_URL` | No | <https://gitlab.com> | GitLab Base URL |
| `GITLAB_SSL_VERIFY` | No | `true` | Whether to verify SSL certs for GitLab API queries |
| `LOG_LEVEL` | No | `INFO` | Log level for Uvicorn |
| `UVICORN_HOST` | No | `0.0.0.0` | Uvicorn host |
| `UVICORN_PORT` | No | `8080` | Uvicorn port |
| `UVICORN_RELOAD` | No | `false` | Uvicorn watches for files changed to reload |

# Development

## Prepare your dev environment

Create a virtual environment for the project:

```bash
$ uv sync
```

## Get a GitLab personal access token

See <https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html>

## Start server

```bash
export GITLAB_TOKEN="<your-personal-access-token>"
export PROJECT_IDS='["one/project","another/project"]'
./dev.sh
```

## Getting metrics

`curl localhost:8080/metrics/`
