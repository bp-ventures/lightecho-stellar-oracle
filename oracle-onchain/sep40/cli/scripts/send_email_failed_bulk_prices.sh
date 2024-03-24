#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR" || exit

FEED_EXIT_CODE=$1
SUBJECT=""
BODY=""

if [[ $FEED_EXIT_CODE == 2 ]]; then
    SUBJECT="Oracle feed failed: insufficient XLM balance"
    BODY="Failed to feed prices into Oracle due to insufficient XLM balance. Use these commands to see the logs:\nsudo machinectl shell lightecho-stellar-oracle@\njournalctl --user -u feed_bulk_from_db\n"
else
    SUBJECT="Oracle feed failed"
    BODY="Failed to feed prices into Oracle. Use these commands to see the logs:\nsudo machinectl shell lightecho-stellar-oracle@\njournalctl --user -u feed_bulk_from_db\n"
fi

echo -e "$BODY" | mutt  -s "$SUBJECT" -- support@bpventures.us
