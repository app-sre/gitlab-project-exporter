#
# Base image with defaults for all stages
FROM registry.access.redhat.com/ubi9/python-312@sha256:b642db8b1f0f9dca7bbe6999db7ac4c96cf3036833fc344af092268afbb02893 AS base

COPY LICENSE /licenses/LICENSE

#
# Builder image
#
FROM base AS builder
COPY --from=ghcr.io/astral-sh/uv:0.5.22@sha256:db7daf75d8f12d1c982df42d9b01519fc8fca98a89a91a7623a088d07408221f /uv /bin/uv

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
