#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR" || exit
echo -e "Failed to feed prices into Oracle. Use these commands to see the logs:\nsudo machinectl shell lightecho-stellar-oracle@\njournalctl --user -u feed_all_from_db\n" | mutt  -s "Oracle feed failed" -- support@bpventures.us
