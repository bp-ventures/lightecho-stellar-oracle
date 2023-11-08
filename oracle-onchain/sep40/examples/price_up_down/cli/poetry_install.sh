#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR" || exit

RED='\033[0;31m'
NC='\033[0m' # No Color

POETRY=poetry
if ! [ command -v $POETRY &>/dev/null ]; then
    if [ -f ~/.local/bin/poetry ]; then
        POETRY=~/.local/bin/poetry
    else
        printf "${RED}Error: program 'poetry' not found. Please check README.md for instructions. Exiting.${NC}\n"
        exit 1
    fi
fi
