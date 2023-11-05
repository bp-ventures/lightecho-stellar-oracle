#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR" || exit
cd ..
~/.local/bin/poetry run python cli.py oracle bump_instance || ./send_email_failed_bump_instance.sh
