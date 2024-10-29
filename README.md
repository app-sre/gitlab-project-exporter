# gitlab-project-exporter

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![PyPI](https://img.shields.io/pypi/v/gitlab-project-exporter)][pypi-link]
[![PyPI platforms][pypi-platforms]][pypi-link]
![PyPI - License](https://img.shields.io/pypi/l/gitlab-project-exporter)

Prometheus exporter for Gitlab Projects

## Metrics exported

|Metric name|Description|
|gitlab_remote_mirror_status|Gitlab [Remote Mirror](https://docs.gitlab.com/ee/api/remote_mirrors.html) status|

## Configuration

| Env variable      | Mandatory | Default                    | Description                                 |
| PROJECT_IDS       | Yes       |                            | Gitlab Project IDS, e.g. '["user/project"]' |
| GITLAB_URL        | No        | https://gitlab.com         | Gitlab base url                             |
| GITLAB_TOKEN      | No        | ""                         | Personal access token                       |
| GITLAB_SSL_VERIFY | No        | true                       | SSL verify for gitlab api queries           |
| LOG_LEVEL         | No        | INFO                       | Log level Uvicorn options                   |
| UVICORN_OPTS      | No        | --host 0.0.0.0 --port 8080 | Uvicorn options                             |

# Development

## Prepare your dev environment

Create a virtual environment for the project:

```bash
$ poetry install
```

## Get a GitLab personal access token

See https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html

## Start server

export PROMETHEUS_MULTIPROC_DIR=$(mktemp -d)
export GITLAB_TOKEN="<your-personal-access-token>"
export PROJECT_IDS='["one/project","another/project"]'
poetry run fastapi dev gitlab_project_exporter/main.py

## Getting metrics

curl localhost:8000/metrics/
