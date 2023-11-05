#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR" || exit
~/.local/bin/poetry run python bump_instance.py || ./send_email_failed_bump_instance.sh
