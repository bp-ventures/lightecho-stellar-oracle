#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR" || exit
echo "Failed to bump Oracle instance. Use these commands to see the logs:\nsudo machinectl shell lightecho-stellar-oracle@\njournalctl --user -u bump_instance\n" | mutt  -s "Oracle bump failed" -- support@bpventures.us
