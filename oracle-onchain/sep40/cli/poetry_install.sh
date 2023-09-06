#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR" || exit

RED='\033[0;31m'
NC='\033[0m' # No Color
command -v "poetry" >/dev/null 2>&1 || { printf "${RED}Error: program 'poetry' not found. Please check README.md instructions. Exiting.${NC}\n"; exit 1; }

poetry install
