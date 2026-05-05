#
# Base image with defaults for all stages
FROM registry.access.redhat.com/ubi9/python-312@sha256:12662c50b0ce52c5a5f43724c9c588c6cbe9be98521f4e3f4112ab01a7becbe5 AS base

COPY LICENSE /licenses/LICENSE

#
# Builder image
#
FROM base AS builder
COPY --from=ghcr.io/astral-sh/uv:0.11.9@sha256:6b6fa841d71a48fbc9e2c55651c5ad570e01104d7a7d701f57b2b22c0f58e9b1 /uv /bin/uv

ENV \
    # use venv from ubi image
    UV_PROJECT_ENVIRONMENT=$APP_ROOT \
    # compile bytecode for faster startup
    UV_COMPILE_BYTECODE="true" \
    # disable uv cache. it doesn't make sense in a container
    UV_NO_CACHE=true

COPY pyproject.toml uv.lock ./
# Test lock file is up to date
RUN uv lock --check
# Install the project dependencies
RUN uv sync --frozen --no-install-project --no-group dev

COPY README.md app.sh ./
COPY gitlab_project_exporter ./gitlab_project_exporter
RUN uv sync --frozen --no-group dev

#
# Test image
#
FROM builder AS test

COPY Makefile ./
RUN uv sync --frozen

COPY tests ./tests
RUN make test

#
# Production image
#
FROM base AS prod
EXPOSE 8080
COPY --from=builder /opt/app-root /opt/app-root
CMD ["/opt/app-root/src/app.sh"]
