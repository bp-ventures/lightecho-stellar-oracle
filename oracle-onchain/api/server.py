from flask import Flask, request
from stellar_sdk import xdr as stellar_xdr
from stellar_sdk.xdr.sc_val_type import SCValType

app = Flask(__name__)


def parse_sc_val(sc_val):
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
        high = sc_val.i128.hi.uint64
        low = sc_val.i128.lo.uint64
        uint128 = (high << 64) | low
        return uint128
    raise ValueError("Could not parse sc_val")


@app.route("/soroban/parse-result-xdr/", methods=["POST"])
def soroban_parse_tx_response():
    if not request.json:
        return {"error": "This endpoint requires a JSON payload"}, 400
    xdr = request.json.get("xdr")
    if not xdr:
        return {"error": "Missing 'xdr' from JSON payload"}, 400
    transaction_meta = stellar_xdr.TransactionMeta.from_xdr(xdr)  # type: ignore
    # TODO handle multiple results[]
    result = transaction_meta.v3.tx_result.result.results[0].tr.invoke_host_function_result.success  # type: ignore
    common_resp = {"type": result.type}
    if result.type == SCValType.SCV_VOID:
        return common_resp
    elif result.type == SCValType.SCV_MAP:
        data = {}
        assert result.map is not None
        for entry in result.map.sc_map:
            key = entry.key.sym.sc_symbol.decode()
            value = parse_sc_val(entry.val)
            data[key] = value
        return {**common_resp, "map": data}
    elif result.type == SCValType.SCV_SYMBOL:
        return {**common_resp, "sym": result.sym.sc_symbol.decode()}
    else:
        return {**common_resp, "error": "Unexpected result type"}, 400
