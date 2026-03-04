#!/usr/bin/env bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR" || exit

set -e
sqlite3 db.sqlite3 "DELETE FROM feed_bulk_from_db_logs WHERE created_at < DATE('now', '-1 months');"
sqlite3 db.sqlite3 ".dump prices" | gzip > "backup_table_prices_$(date +\%Y\%m\%d).sql.gz"
sqlite3 db.sqlite3 "DELETE FROM prices WHERE created_at < DATE('now', '-6 months');"
sqlite3 db.sqlite3 "VACUUM;"
set +e
