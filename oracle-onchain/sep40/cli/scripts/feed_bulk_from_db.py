import sqlite3
import logging
import importlib.util
import base64
import json
from datetime import datetime
import sys
import subprocess
import math
from contextlib import contextmanager
from typing import List, Dict, Tuple
from pathlib import Path

RESOLUTION = 600
EXIT_CODE_INSUFFICIENT_BALANCE = 2

mod_spec = importlib.util.spec_from_file_location(
    "local_settings", Path(__file__).resolve().parent.parent / "local_settings.py"
)
assert mod_spec
local_settings = importlib.util.module_from_spec(mod_spec)
sys.modules["local_settings"] = local_settings
assert mod_spec.loader
mod_spec.loader.exec_module(local_settings)

db_path = getattr(local_settings, "API_DB_PATH", None)
if db_path is None:
    db_path = (
        Path(__file__).parent.parent.parent.parent.resolve() / "api" / "db.sqlite3"
    )
cli_dir = Path(__file__).parent.parent.resolve()

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s %(filename)s:%(lineno)d %(levelname)s] %(message)s",
)
logger = logging.getLogger("feed_bulk_from_db.py")


def run_cli(cmd: str) -> Tuple[int, str]:
    try:
        return 0, subprocess.check_output(
            f"./cli {cmd}", shell=True, text=True, cwd=cli_dir, stderr=subprocess.STDOUT
        )
    except subprocess.CalledProcessError as e:
        return e.returncode, e.output


@contextmanager
def cursor_ctx():
    conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        yield cursor
    except Exception as e:
        conn.rollback()
        raise e
    else:
        conn.commit()
    finally:
        conn.close()


def get_closest_past_timestamp(external_timestamp, resolution):
    # Calculate the closest past timestamp that preserves the resolution
    adjusted_timestamp = math.floor(external_timestamp / resolution) * resolution
    return adjusted_timestamp


def list_to_base64(data_list):
    json_str = json.dumps(data_list)
    json_bytes = json_str.encode("utf-8")
    return base64.b64encode(json_bytes).decode("utf-8")


def log_result_to_db(cmd, success, output):
    query = """
        INSERT INTO feed_bulk_from_db_logs
        (
            command,
            output,
            success
        )
        VALUES
        (
            :command,
            :output,
            :success
        )
    """
    with cursor_ctx() as cursor:
        cursor.execute(
            query,
            {
                "command": cmd,
                "output": output,
                "success": success,
            },
        )


def add_prices_to_blockchain(prices: List[Dict], timestamp: int):
    logger.info(
        f"Adding {len(prices)} prices to the blockchain with timestamp {timestamp}"
    )
    xlm_based_prices = []
    usd_based_prices = []
    source_symbols = {}
    for price in prices:
        parsed_price = {
            "source": price["source"],
            "asset_type": "other",
            "asset": price["buy_asset"],
            "price": price["price"],
            "timestamp": timestamp,
        }
        source_symbols.setdefault(price["source"], []).append(price["symbol"])
        if price["sell_asset"] == "XLM":
            xlm_based_prices.append(parsed_price)
        elif price["sell_asset"] == "USD":
            usd_based_prices.append(parsed_price)
        else:
            raise ValueError(f"Unexpected price sell_asset: {price['sell_asset']}")
    if xlm_based_prices:
        cmd = f"--oracle-contract-id {local_settings.ORACLE_CONTRACT_ID} oracle add_prices_base64 {list_to_base64(xlm_based_prices)}"
        logger.info(f"cli.py {cmd}")
        returncode, output = run_cli(cmd)
        logger.info(output)
        if returncode == EXIT_CODE_INSUFFICIENT_BALANCE:
            sys.exit(EXIT_CODE_INSUFFICIENT_BALANCE)
        is_success = returncode == 0
        log_result_to_db(cmd, is_success, output)
    if usd_based_prices:
        logger.warning("Skipping adding USD-based prices, as they're not supported in the blockchain contract yet")
    for source, symbols in source_symbols.items():
        mark_symbols_as_added_to_blockchain(source, symbols)


def mark_symbols_as_added_to_blockchain(source, symbols):
    placeholders = ", ".join(["?"] * len(symbols))
    query = f"UPDATE prices SET added_to_blockchain = 1 WHERE source = ? AND symbol IN ({placeholders})"
    with cursor_ctx() as cursor:
        cursor.execute(query, [source] + symbols)


def get_latest_time_prices_were_added_to_blockchain():
    query = """
        SELECT
            id,
            created_at
        FROM feed_bulk_from_db_logs
        WHERE success = TRUE
        ORDER BY created_at DESC LIMIT 1
    """
    with cursor_ctx() as cursor:
        cursor.execute(query)
        row = cursor.fetchone()
        if not row:
            return None
        row_dict = dict(row)
        return row_dict["created_at"]


def read_prices_from_db():
    query = """
        SELECT
            id,
            updated_at,
            source,
            symbol,
            price,
            sell_asset,
            buy_asset
        FROM prices
        WHERE status = 'active'
          AND asset_type = 'other'
          AND added_to_blockchain = 0
        ORDER BY updated_at DESC
    """
    with cursor_ctx() as cursor:
        cursor.execute(query)
        prices_from_db = []
        symbols = {}

        for price in cursor.fetchall():
            prices_from_db.append(dict(price))

        latest_time_prices_were_added_to_blockchain = (
            get_latest_time_prices_were_added_to_blockchain()
        )
        if latest_time_prices_were_added_to_blockchain is None:
            latest_time_prices_were_added_to_blockchain = datetime(1970, 1, 1)
        last_time_prices_were_added_to_blockchain_timestamp = (
            latest_time_prices_were_added_to_blockchain.timestamp()
        )
        current_unix_time = int(datetime.now().timestamp())
        closest_past_normalized_timestamp = get_closest_past_timestamp(
            current_unix_time, RESOLUTION
        )
        if (
            last_time_prices_were_added_to_blockchain_timestamp
            >= closest_past_normalized_timestamp
        ):
            logger.info(
                "prices were already added to the blockchain for the current resolution"
            )
            return

        batches_of_prices_to_feed = []
        prices_to_feed = []
        for price in prices_from_db:
            if len(prices_to_feed) >= 10:
                batches_of_prices_to_feed.append(prices_to_feed)
                prices_to_feed = []
                continue
            if price["source"] not in symbols:
                symbols[price["source"]] = []
            if price["symbol"] in symbols[price["source"]]:
                continue
            prices_to_feed.append(price)
            symbols[price["source"]].append(price["symbol"])
        if prices_to_feed:
            batches_of_prices_to_feed.append(prices_to_feed)
        if len(batches_of_prices_to_feed) == 0:
            logger.info("no new prices to feed into the blockchain contract")
        else:
            for batch in batches_of_prices_to_feed:
                add_prices_to_blockchain(batch, closest_past_normalized_timestamp)


if __name__ == "__main__":
    read_prices_from_db()
