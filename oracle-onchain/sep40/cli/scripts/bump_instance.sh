#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR" || exit
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
timeout 30s $POETRY run python bump_instance.py

if [ $? -ne 0 ]; then
    echo "Failed to bump instance"
    ./send_email_failed_bump_instance.sh
    exit 1
fi
