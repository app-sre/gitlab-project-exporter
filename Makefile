CODE_ROOT := gitlab_project_exporter
BUILD_ARGS := POETRY_VERSION=1.8.3
CONTAINER_ENGINE ?= $(shell which podman >/dev/null 2>&1 && echo podman || echo docker)
IMAGE_NAME ?= gitlab-project-exporter
IMAGE_TAG ?= $(shell git rev-parse --short=7 HEAD)

format:
	poetry run ruff check
	poetry run ruff format
.PHONY: format

test:
	poetry run ruff check --no-fix
	poetry run ruff format --check
	poetry run mypy
	poetry run pytest -vv --cov=gitlab_project_exporter --cov-report=term-missing --cov-report xml
.PHONY: test

container:
	$(CONTAINER_ENGINE) build -t $(IMAGE_NAME):$(IMAGE_TAG) $(foreach arg,$(BUILD_ARGS),--build-arg $(arg)) .
.PHONY: container

container-test:
	$(CONTAINER_ENGINE) build --target test -t $(IMAGE_NAME):test-$(IMAGE_TAG) $(foreach arg,$(BUILD_ARGS),--build-arg $(arg)) .
.PHONY: container-test
