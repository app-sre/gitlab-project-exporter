FROM registry.access.redhat.com/ubi9/ubi-minimal:9.5-1734497536@sha256:daa61d6103e98bccf40d7a69a0d4f8786ec390e2204fd94f7cc49053e9949360 as base-python
COPY LICENSE /licenses/LICENSE
ENV PYTHONUNBUFFERED=1

RUN microdnf upgrade -y && \
    microdnf install -y \
        shadow-utils \
        python3.11 && \
    microdnf clean all && \
    update-alternatives --install /usr/bin/python3 python /usr/bin/python3.11 1 && \
    ln -snf /usr/bin/python3.11 /usr/bin/python && \
    python3 -m ensurepip

WORKDIR /code
RUN useradd -u 5000 app && chown -R app:app /code

# ---- Interims image to get and build all the python dependencies ----
FROM base-python as build-base-python
ENV POETRY_HOME=/opt/poetry \
    POETRY_VIRTUALENVS_CREATE=false \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PATH=/opt/poetry/bin:$PATH

# install poetry
ARG POETRY_VERSION
RUN POETRY_VERSION=$POETRY_VERSION python3 - < <(curl -sSL https://install.python-poetry.org) && poetry --version

# required for poetry to install the dependencies
COPY --chown=app:app pyproject.toml poetry.lock README.md /code/
# the code
COPY --chown=app:app gitlab_project_exporter /code/gitlab_project_exporter/
COPY --chown=app:app app.sh /code/

# install the python dependencies
RUN poetry install --no-interaction --no-ansi --only main

# ---- Test image ----
FROM build-base-python as test
# install the test dependencies
RUN microdnf install -y make
RUN poetry install --no-interaction --no-ansi
# install the tests
COPY --chown=app:app tests /code/tests/
COPY --chown=app:app Makefile /code/
USER app:app
RUN make test

# ---- Bundle everything together in the final image ----
FROM base-python
EXPOSE 8080

# get all the python dependencies from the build-python stage
COPY --from=build-base-python /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=build-base-python /usr/local/lib64/python3.11/site-packages/ /usr/local/lib64/python3.11/site-packages/
COPY --from=build-base-python /usr/local/bin/ /usr/local/bin/
COPY --from=build-base-python /code/ /code/

USER app:app
CMD ["/code/app.sh"]
