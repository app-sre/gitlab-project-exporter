#!/bin/bash

export PROMETHEUS_MULTIPROC_DIR=$(mktemp -d)
trap "rm -rf $PROMETHEUS_MULTIPROC_DIR" INT TERM EXIT
export UVICORN_RELOAD="true"
export LOG_LEVEL=DEBUG

poetry run python gitlab_project_exporter/main.py
