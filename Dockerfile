#
# Base image with defaults for all stages
FROM registry.access.redhat.com/ubi9/python-312@sha256:7eff0198911e53c3c67634e82e6c156e3bd491149721e998280f104b7a185772 AS base

COPY LICENSE /licenses/LICENSE

#
# Builder image
#
FROM base AS builder
COPY --from=ghcr.io/astral-sh/uv:0.6.0@sha256:63b7453435641145dc3afab79a6bc2b6df6f77107bec2d0df39fd27b1c791c0a /uv /bin/uv

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
