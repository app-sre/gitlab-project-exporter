#!/bin/bash

export PROMETHEUS_MULTIPROC_DIR=$(mktemp -d)
trap "rm -rf $PROMETHEUS_MULTIPROC_DIR" INT TERM EXIT
export UVICORN_HOST="0.0.0.0"
exec python gitlab_project_exporter/main.py
