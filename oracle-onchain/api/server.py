from decimal import Decimal
import importlib.util
from pathlib import Path
from subprocess import check_output
from contextlib import contextmanager
import sys
from typing import Optional
import sqlite3

from flask import Flask, Response, request
from flask_cors import CORS
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash

mod_spec = importlib.util.spec_from_file_location(
    "local_settings", Path(__file__).resolve().parent / "local_settings.py"
)
assert mod_spec
local_settings = importlib.util.module_from_spec(mod_spec)
sys.modules["local_settings"] = local_settings
assert mod_spec.loader
mod_spec.loader.exec_module(local_settings)


auth = HTTPBasicAuth()
auth.error_handler(lambda status: ({"error": "Unauthorized"}, status))
db_path = getattr(local_settings, "DB_PATH", None)
if db_path is None:
    db_path = Path(__file__).parent.resolve() / "db.sqlite3"


@contextmanager
def cursor_ctx():
    conn = sqlite3.connect(db_path)
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


def db_create_tables():
    with cursor_ctx() as cursor:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS prices (
                id          INTEGER PRIMARY KEY,
                created_at  TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
                updated_at  TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
                timeframe   TEXT,
                status      TEXT,
                source      INTEGER NOT NULL,
                asset_type  TEXT NOT NULL,
                symbol      TEXT NOT NULL,
                price       TEXT NOT NULL,
                bid         TEXT NOT NULL,
                offer       TEXT NOT NULL,
                sell_asset  TEXT NOT NULL,
                buy_asset   TEXT NOT NULL,
                added_to_blockchain BOOLEAN DEFAULT 0
            )
            """
        )


def init_app():
    """Initialize the core application."""
    app = Flask(__name__)
    CORS(app)
    db_create_tables()
    return app


app = init_app()


@auth.verify_password
def verify_password(username, password):
    if username in local_settings.API_USERS and check_password_hash(
        local_settings.API_USERS.get(username), password
    ):
        return username


@app.before_request
def handle_options():
    if request.method.lower() == "options":
        return Response()


def parse_symbol(symbol: Optional[str] = None):
    if symbol is None:
        return None, None, "Missing payload field 'symbol'"
    bases = local_settings.CONTRACTS.keys()
    for base in bases:
        parts = symbol.split(base)
        if len(parts) == 2:
            return base, parts[1], None
    return None, None, "Invalid 'symbol', must begin with one of: {', '.join(bases)}"


def parse_source(source: Optional[str] = None):
    if source is None:
        return None, "Missing payload field 'source'"
    try:
        int(source)
        return str(source), None
    except (ValueError, TypeError):
        return None, "Invalid 'source', must be an integer"


def parse_price(price: Optional[str] = None):
    if price is None:
        return None, "Missing payload field 'price'"
    try:
        price_d = Decimal(price)
        return str(price_d), None
    except (ValueError, TypeError):
        return None, "Invalid 'source', must be an integer"


def parse_asset_type(asset_type: Optional[str] = None):
    if asset_type is None:
        return None, "Missing payload field 'asset_type'"
    supported_asset_types = ["stellar", "other"]
    if asset_type not in supported_asset_types:
        return (
            None,
            f"Invalid 'asset_type', must be one of: {', '.join(supported_asset_types)}",
        )
    return asset_type, None


def read_prices_from_db():
    query = """
        SELECT
            id,
            updated_at,
            symbol,
            added_to_blockchain
        FROM prices
        WHERE added_to_blockchain = 1
        ORDER BY updated_at DESC
    """
    with cursor_ctx() as cursor:
        cursor.execute(query)
        prices = []
        symbols = []
        for result in cursor.fetchall():
            result_dict = dict(result)
            if result_dict["symbol"] in symbols:
                continue
            prices.append(result_dict)
            symbols.append(result_dict["symbol"])
        return prices

@app.route("/soroban/add-price/", methods=["POST", "OPTIONS"])
@auth.login_required
def add_price():
    data = request.json
    if not data:
        return {"error": "This endpoint requires a JSON payload"}, 400
    source, err = parse_source(data.get("source"))
    if err:
        return {"error": err}
    asset_type, err = parse_asset_type(data.get("asset_type"))
    if err:
        return {"error": err}
    base, quote, err = parse_symbol(data.get("symbol"))
    if err:
        return {"error": err}
    price, err = parse_price(data.get("price"))
    if err:
        return {"error": err}
    contract_id = local_settings.CONTRACTS[base]

    cli_dir = Path(__file__).parent.parent / "v2" / "cli"
    cmd = [
        "./cli",
        "--contract-id",
        contract_id,
        "add-price",
        source,
        asset_type,
        quote,
        price,
    ]
    print(cmd)
    raw_output = check_output(cmd, cwd=cli_dir)
    output = raw_output.decode()
    return {"success": True, "output": output}


@app.route("/db/add-prices/", methods=["POST", "OPTIONS"])
@auth.login_required
def api_db_add_prices():
    data = request.json
    if not data:
        return {"error": "This endpoint requires a JSON payload"}, 400
    if not isinstance(data, list):
        return {
            "error": "The payload must be a list, each item of the list being a price entry object"
        }, 400
    with cursor_ctx() as cursor:
        for item in data:
            cursor.execute(
                """
            INSERT INTO prices (
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
            ) VALUES (
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?
            )
            """,
                (
                    item["timeframe"],
                    item["status"],
                    item["source"],
                    item["asset_type"],
                    item["symbol"],
                    item["price"],
                    item["bid"],
                    item["offer"],
                    item["sell_asset"],
                    item["buy_asset"],
                ),
            )
    return {"data": read_prices_from_db()}


def get_enum_variable_name(enum_class, value):
    for name, member in enum_class.__members__.items():
        if member.value == value:
            return name
    raise ValueError(f"Value {value} not found in the {enum_class.__name__} IntEnum.")
