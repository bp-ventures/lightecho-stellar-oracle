#!/usr/bin/env -S poetry run python
import sqlite3
import importlib.util
import sys
import subprocess
import math
import multiprocessing
from contextlib import contextmanager
from pathlib import Path

CONTRACT_ID_XLM = "CDYHDC7OPAWPQ46TGT5PU77C2NWFGERD6IQRKVNBL34HCXHARWO24XWM"
CONTRACT_ID_USD = "CAC6JWJG22ULRNGY75H2NVDIXQQP5JRJPERTZXXXONJHD2ETMGGEV7WP"
RESOLUTION = 10800

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
    db_path = Path(__file__).parent.parent.parent.parent.resolve() / "api" / "db.sqlite3"
cli_dir = Path(__file__).parent.parent.resolve()


def run_cli(cmd: str):
    return subprocess.check_output(
        f"./cli {cmd}", shell=True, text=True, cwd=cli_dir
    )


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


def adjust_timestamp(external_timestamp, resolution):
    # Calculate the closest future timestamp that preserves the resolution
    adjusted_timestamp = math.ceil(external_timestamp / resolution) * resolution
    return adjusted_timestamp


def read_prices_from_db():
    query = """
        SELECT
            id,
            created_at,
            updated_at,
            timeframe,
            status,
            source,
            asset_type,
            symbol,
            price,
            bid,
            offer,
            sell_asset,
            buy_asset
        FROM prices
        ORDER BY updated_at DESC
    """
    with cursor_ctx() as cursor:
        cursor.execute(query)
        prices = []
        symbols = []
        for result in cursor.fetchall():
            result_dict = dict(result)
            if result_dict['symbol'] not in symbols:
                symbols.append(result_dict['symbol'])
                timestamp_as_unix = int(result_dict['updated_at'].timestamp())
                result_dict['adjusted_timestamp'] = adjust_timestamp(timestamp_as_unix, RESOLUTION)
                prices.append(result_dict)
        for price in prices:
            if price['sell_asset'] == "XLM":
                contract_id = CONTRACT_ID_XLM
            elif price['sell_asset'] == 'USD':
                contract_id = CONTRACT_ID_USD
            else:
                raise ValueError(f"Unexpected price sell_asset: {price['sell_asset']}")
            output = run_cli(
                    f"--oracle-contract-id {contract_id} oracle add_price 1 other {price['buy_asset']} {price['price']}"
            )
            print(output)

if __name__ == "__main__":
    read_prices_from_db()

