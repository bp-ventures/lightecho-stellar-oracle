#!/usr/bin/env bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR" || exit
set -a
source .env || exit
set +a
exec poetry run python -m gunicorn --bind "$GUNICORN_BIND" --workers "$GUNICORN_WORKERS" --timeout "$GUNICORN_TIMEOUT" server:app
