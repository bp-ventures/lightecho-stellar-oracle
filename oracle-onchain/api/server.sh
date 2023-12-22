#!/usr/bin/env bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR" || exit
set -a
source .env || exit
set +a
if [ -f ~/.local/bin/poetry ]; then
    POETRY=~/.local/bin/poetry
else
    POETRY=poetry
    command $POETRY &>/dev/null
    if [ $? -ne 0 ]; then
        printf "${RED}Error: program 'poetry' not found. Please check README.md for instructions. Exiting.${NC}\n"
        exit 1
    fi
fi
$POETRY run python -m gunicorn --bind "$GUNICORN_BIND" --workers "$GUNICORN_WORKERS" --timeout "$GUNICORN_TIMEOUT" server:app
