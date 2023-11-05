#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR" || exit

~/.local/bin/poetry run python feed_all_from_db.py || ./send_email_failed_feed_prices.sh
