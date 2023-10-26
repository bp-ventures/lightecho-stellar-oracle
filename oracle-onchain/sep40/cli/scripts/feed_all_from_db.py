#!/usr/bin/env -S poetry run python
import sqlite3
import importlib.util
import sys
from contextlib import contextmanager
from pathlib import Path

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

@contextmanager
def cursor_ctx():
    conn = sqlite3.connect(db_path)
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
                prices.append(result_dict)
        #TODO do something with prices

if __name__ == "__main__":
    read_prices_from_db()
