#!/bin/bash

export PROMETHEUS_MULTIPROC_DIR=$(mktemp -d)

trap "rm -rf $PROMETHEUS_MULTIPROC_DIR" INT TERM EXIT

UVICORN_OPTS="${UVICORN_OPTS:- --host 0.0.0.0 --port 8080}"

echo "---> Serving application with uvicorn ..."
exec uvicorn $UVICORN_OPTS "$@" gitlab_project_exporter.main:app
