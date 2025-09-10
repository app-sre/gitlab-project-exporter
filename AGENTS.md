# CLAUDE.md

This file provides guidance to AI development tools when working with code in this repository.

## Project Overview

This is a **Prometheus exporter for GitLab projects** that monitors remote mirror status across multiple GitLab projects. The application exposes metrics in Prometheus format that can be scraped by monitoring systems to track the health of GitLab remote mirrors.

**Key Purpose:**
- Monitor GitLab remote mirror synchronization status
- Provide Prometheus metrics for observability and alerting
- Support multiple projects with concurrent API calls for performance

**Main Metric:**
- `gitlab_remote_mirror_status` - Tracks mirror status (0=OK, 1=Failed) with project, mirror ID, and URL labels

The exporter is built with Python using FastAPI and runs as a containerized web service that periodically fetches mirror status from the GitLab API.

## Development Commands

### Environment Setup
- `uv sync` - Install dependencies and create virtual environment
- `make dev-env` - Alias for `uv sync`

### Development Server
- `./dev.sh` - Start development server with debug logging and auto-reload

### Production Server
- `./app.sh` - Start production server

### Code Quality & Testing
- `make test` - Run full test suite (lock check, ruff lint/format, mypy, pytest with coverage)
- `make format` - Run ruff check and format
- `uv run ruff check` - Lint code
- `uv run ruff format` - Format code
- `uv run mypy` - Type checking
- `uv run pytest -vv --cov=gitlab_project_exporter --cov-report=term-missing --cov-report xml` - Run tests with coverage

### Container Operations
- `make build` - Build production container image
- `make container-test` - Build and run tests in container

## Project Architecture

### Core Components

**FastAPI Application** (`gitlab_project_exporter/server.py:38`)
- Main app factory creates FastAPI instance with health endpoint and metrics mounting
- Prometheus metrics exposed at `/metrics` endpoint
- Health check at `/healthz`

**Configuration** (`gitlab_project_exporter/config.py:4`)
- Pydantic BaseSettings for environment-based configuration
- Required: `PROJECT_IDS` (list of GitLab project IDs)
- Optional: GitLab URL, SSL verification, logging, Uvicorn settings

**Prometheus Collector** (`gitlab_project_exporter/collector.py:34`)
- `GitLabProjectCollector` implements Prometheus Collector interface
- Uses ThreadPoolExecutor for concurrent GitLab API calls
- Collects remote mirror status metrics for specified projects

**GitLab Integration** (`gitlab_project_exporter/gitlab_project.py:32`)
- `GitlabProject` wraps python-gitlab client
- Fetches remote mirror status and converts to metric values
- Status mapping: failed/to_retry/none → 1, others → 0

### Key Environment Variables
- `GITLAB_TOKEN` - GitLab personal access token (required for dev)
- `PROJECT_IDS` - JSON array of project IDs (required)
- `GITLAB_URL` - GitLab instance URL (default: https://gitlab.com)
- `UVICORN_RELOAD` - Enable auto-reload for development

### Metrics Exported
- `gitlab_remote_mirror_status` - Gauge with labels: project_id, mirror_id, mirror_url

### Dependencies
- FastAPI + Uvicorn for web server
- python-gitlab for GitLab API interaction
- prometheus-client for metrics collection
- Pydantic for configuration and data validation

### Test Coverage
- Minimum coverage requirement: 85%
- Tests located in `tests/` directory
- Uses pytest with mocking via pytest-mock and responses
- All tests must pass for CI/CD pipeline
