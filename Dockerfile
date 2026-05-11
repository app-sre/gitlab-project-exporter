#
# Base image with defaults for all stages
FROM registry.access.redhat.com/ubi9/python-312@sha256:bf2f5a3cf0c1542d2c90e729bef7e79df746e0331ab7fd19c86e3ff4792dc9f5 AS base

COPY LICENSE /licenses/LICENSE

#
# Builder image
#
FROM base AS builder
COPY --from=ghcr.io/astral-sh/uv:0.11.13@sha256:841c8e6fe30a8b07b4478d12d0c608cba6de66102d29d65d1cc423af86051563 /uv /bin/uv

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
