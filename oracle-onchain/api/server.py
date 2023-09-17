from decimal import Decimal
import importlib.util
from pathlib import Path
from subprocess import check_output
import sys
from typing import Optional

from flask import Flask, Response, request
from flask_cors import CORS
from flask_httpauth import HTTPBasicAuth
from stellar_sdk import xdr as stellar_xdr
from stellar_sdk.xdr.sc_val_type import SCValType
from werkzeug.security import check_password_hash

mod_spec = importlib.util.spec_from_file_location(
    "local_settings", Path(__file__).resolve().parent / "local_settings.py"
)
assert mod_spec
local_settings = importlib.util.module_from_spec(mod_spec)
sys.modules["local_settings"] = local_settings
assert mod_spec.loader
mod_spec.loader.exec_module(local_settings)


app = Flask(__name__)
auth = HTTPBasicAuth()
auth.error_handler(lambda status: ({"error": "Unauthorized"}, status))
CORS(app)


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


@app.route("/soroban/add-price/", methods=["POST", "OPTIONS"])
@auth.login_required
def set_rate():
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


def parse_sc_val(sc_val):
    if sc_val.type == SCValType.SCV_BOOL:
        return sc_val.b
    if sc_val.u32 is not None:
        return sc_val.u32.uint32
    if sc_val.i32 is not None:
        return sc_val.i32.int32
    if sc_val.u64 is not None:
        return sc_val.u64.uint64
    if sc_val.i64 is not None:
        return sc_val.i64.int64
    if sc_val.u128 is not None:
        high = sc_val.u128.hi.uint64
        low = sc_val.u128.lo.uint64
        uint128 = (high << 64) | low
        return uint128
    if sc_val.i128 is not None:
        high = sc_val.i128.hi.int64
        low = sc_val.i128.lo.uint64
        uint128 = (high << 64) | low
        return uint128
    if sc_val.map is not None:
        return parse_sc_map(sc_val.map.sc_map)
    if sc_val.vec is not None:
        return parse_sc_vec(sc_val.vec)
    if sc_val.sym is not None:
        return sc_val.sym.sc_symbol.decode()
    raise ValueError("Could not parse sc_val")


def parse_sc_vec(sc_vec):
    vec = []
    for val in sc_vec.sc_vec:
        vec.append(parse_sc_val(val))
    return vec


def parse_sc_map(sc_map):
    data = {}
    for entry in sc_map:
        key = entry.key.sym.sc_symbol.decode()
        value = parse_sc_val(entry.val)
        data[key] = value
    return data


def get_enum_variable_name(enum_class, value):
    for name, member in enum_class.__members__.items():
        if member.value == value:
            return name
    raise ValueError(f"Value {value} not found in the {enum_class.__name__} IntEnum.")


@app.route("/soroban/parse-result-xdr/", methods=["POST", "OPTIONS"])
def soroban_parse_tx_response():
    if not request.json:
        return {"error": "This endpoint requires a JSON payload"}, 400
    xdr = request.json.get("xdr")
    if not xdr:
        return {"error": "Missing 'xdr' from JSON payload"}, 400
    transaction_meta = stellar_xdr.TransactionMeta.from_xdr(xdr)  # type: ignore
    # TODO handle multiple results[]
    assert transaction_meta.v3.soroban_meta
    result = transaction_meta.v3.soroban_meta.return_value
    common_resp = {"type": get_enum_variable_name(SCValType, result.type)}
    if result.type == SCValType.SCV_VOID:
        return common_resp
    elif result.type == SCValType.SCV_MAP:
        assert result.map is not None
        return {**common_resp, "value": parse_sc_map(result.map.sc_map)}
    elif result.type in [
        SCValType.SCV_U32,
        SCValType.SCV_I32,
        SCValType.SCV_U64,
        SCValType.SCV_I64,
        SCValType.SCV_U128,
        SCValType.SCV_I128,
        SCValType.SCV_SYMBOL,
    ]:
        return {**common_resp, "value": parse_sc_val(result)}
    elif result.type == SCValType.SCV_ADDRESS:
        return {**common_resp, "value": str(result.address)}
    elif result.type == SCValType.SCV_SYMBOL:
        return {**common_resp, "value": result.sym.sc_symbol.decode()}
    elif result.type == SCValType.SCV_VEC:
        return {**common_resp, "value": parse_sc_vec(result.vec)}
    else:
        return {**common_resp, "error": "Unexpected result type"}, 400


@app.route("/soroban/int-to-uint64-high-low/", methods=["POST", "OPTIONS"])
def soroban_int_to_uint64():
    if not request.json:
        return {"error": "This endpoint requires a JSON payload"}, 400
    value = request.json.get("value")
    if not value:
        return {"error": "Missing 'value' from JSON payload"}, 400
    try:
        value_int = int(value)
    except (ValueError, TypeError):
        return {"error": "'value' must be a valid integer"}, 400
    high = (value_int >> 32) & 0xFFFFFFFF
    low = value_int & 0xFFFFFFFF
    return {"high": high, "low": low}
