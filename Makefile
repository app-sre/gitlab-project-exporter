CONTAINER_ENGINE ?= $(shell which podman >/dev/null 2>&1 && echo podman || echo docker)
IMAGE_NAME ?= gitlab-project-exporter
IMAGE_TAG ?= $(shell git rev-parse --short=7 HEAD)

format:
	uv run ruff check
	uv run ruff format
.PHONY: format

test:
	uv lock --locked
	uv run ruff check --no-fix
	uv run ruff format --check
	uv run mypy
	uv run pytest -vv --cov=gitlab_project_exporter --cov-report=term-missing --cov-report xml
.PHONY: test

build:
	$(CONTAINER_ENGINE) build -t $(IMAGE_NAME):$(IMAGE_TAG) --target prod .
	$(CONTAINER_ENGINE) tag $(IMAGE_NAME):$(IMAGE_TAG) $(IMAGE_NAME):latest
.PHONY: build

container-test:
	$(CONTAINER_ENGINE) build --target test -t $(IMAGE_NAME):test-$(IMAGE_TAG) $(foreach arg,$(BUILD_ARGS),--build-arg $(arg)) .
.PHONY: container-test

.PHONY: dev-env
dev-env:
	uv sync
