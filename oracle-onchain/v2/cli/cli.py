#!/usr/bin/env -S poetry run python
from decimal import Decimal
import enum
import importlib.util
import json
from pathlib import Path
import sys
import time
from typing import Optional

from colorama import init as colorama_init
from colorama import Fore
from colorama import Style
from stellar_sdk import (
    InvokeHostFunction,
    Keypair,
    StrKey,
    TransactionBuilder,
    TransactionEnvelope,
)
from stellar_sdk import xdr as stellar_xdr
from stellar_sdk.soroban.authorization_entry import AuthorizationEntry
from stellar_sdk.soroban.server import SorobanServer
from stellar_sdk.soroban.soroban_rpc import GetTransactionStatus, SendTransactionStatus
from stellar_sdk.soroban.types import (
    Address,
    Bytes,
    Enum,
    Int128,
    Symbol,
    Uint32,
    Uint64,
)
from stellar_sdk.xdr.sc_val_type import SCValType
import typer

mod_spec = importlib.util.spec_from_file_location(
    "local_settings", Path(__file__).resolve().parent / "local_settings.py"
)
assert mod_spec
local_settings = importlib.util.module_from_spec(mod_spec)
sys.modules["local_settings"] = local_settings
assert mod_spec.loader
mod_spec.loader.exec_module(local_settings)

MAX_DECIMAL_PLACES = 18

colorama_init()
app = typer.Typer()
state = {
    "verbose": False,
    "source_secret": local_settings.SOURCE_SECRET,
    "rpc_server_url": local_settings.RPC_SERVER_URL,
    "contract_id": StrKey.decode_contract(local_settings.CONTRACT_ID).hex(),
    "network_passphrase": local_settings.NETWORK_PASSPHRASE,
    "horizon_url": "https://horizon-futurenet.stellar.org",
}
state["kp"] = Keypair.from_secret(state["source_secret"])
state["soroban_server"] = SorobanServer(state["rpc_server_url"])
state["source_acc"] = state["soroban_server"].load_account(state["kp"].public_key)


class AssetType(enum.Enum):
    stellar = "stellar"
    other = "other"


def print_error(msg: str):
    print(Fore.RED + msg + Style.RESET_ALL)


def abort(msg: str):
    print_error(msg)
    raise typer.Exit()


def vprint(msg: str):
    if state["verbose"]:
        print(msg)


def send_tx(tx: TransactionEnvelope, sign_func=None):
    vprint(f"preparing transaction: {tx.to_xdr()}")
    import pdb; pdb.set_trace()
    tx = state["soroban_server"].prepare_transaction(tx)
    vprint(f"prepared transaction: {tx.to_xdr()}")

    if sign_func is not None:
        sign_func(tx)

    tx.sign(state["kp"])

    send_transaction_data = state["soroban_server"].send_transaction(tx)
    vprint(f"sent transaction: {send_transaction_data}")
    if send_transaction_data.status != SendTransactionStatus.PENDING:
        raise RuntimeError(f"Failed to send transaction: {send_transaction_data}")

    tx_hash = send_transaction_data.hash
    return tx_hash, wait_tx(tx_hash)


def wait_tx(tx_hash: str):
    while True:
        vprint("waiting for transaction to be confirmed...")
        get_transaction_data = state["soroban_server"].get_transaction(tx_hash)
        if get_transaction_data.status != GetTransactionStatus.NOT_FOUND:
            break
        time.sleep(3)
    return get_transaction_data


def invoke_contract_function(function_name, parameters=[], sign_func=None):
    tx = (
        TransactionBuilder(
            state["source_acc"],
            state["network_passphrase"],
            base_fee=300000,
        )
        .set_timeout(30)
        .append_invoke_contract_function_op(
            state["contract_id"],
            function_name,
            parameters,
        )
        .build()
    )

    tx_hash, tx_data = send_tx(tx, sign_func=sign_func)
    vprint(f"transaction: {tx_data}")

    if tx_data.status != GetTransactionStatus.SUCCESS:
        abort(f"Error: {tx_data}")

    return tx_hash, tx_data


def is_tx_success(tx_data):
    return tx_data.status == GetTransactionStatus.SUCCESS


def parse_tx_result(tx_data):
    assert tx_data.result_meta_xdr is not None
    transaction_meta = stellar_xdr.TransactionMeta.from_xdr(tx_data.result_meta_xdr)  # type: ignore
    results = transaction_meta.v3.tx_result.result.results[0].tr.invoke_host_function_result.success  # type: ignore
    return results[0]  # type: ignore


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
        high = sc_val.i128.hi.int64
        low = sc_val.i128.lo.uint64
        int128 = (high << 64) | low
        return int128
    if sc_val.sym is not None:
        return sc_val.sym.sc_symbol.decode()
    if sc_val.map is not None:
        parsed_map = {}
        for map_entry in sc_val.map.sc_map:
            parsed_map[parse_sc_val(map_entry.key)] = parse_sc_val(map_entry.val)
        return parsed_map
    raise ValueError("Could not parse sc_val")


def parse_sc_vec(sc_vec):
    vec = []
    for val in sc_vec.sc_vec:
        vec.append(parse_sc_val(val))
    return vec


def output_tx_data(tx_data):
    vprint(f"transaction: {tx_data}")
    if is_tx_success(tx_data):
        result = parse_tx_result(tx_data)
        if result.type == SCValType.SCV_VOID:
            print("<void>")
        elif result.type == SCValType.SCV_MAP:
            data = {}
            assert result.map is not None
            for entry in result.map.sc_map:
                key = entry.key.sym.sc_symbol.decode()
                value = parse_sc_val(entry.val)
                data[key] = value
            print(json.dumps(data, indent=2))
        elif result.type in [
            SCValType.SCV_U32,
            SCValType.SCV_I32,
            SCValType.SCV_U64,
            SCValType.SCV_I64,
            SCValType.SCV_U128,
            SCValType.SCV_I128,
            SCValType.SCV_SYMBOL,
        ]:
            print(parse_sc_val(result))
        elif result.type == SCValType.SCV_ADDRESS:
            print(str(result.address))
        elif result.type == SCValType.SCV_VEC:
            print(parse_sc_vec(result.vec))
        else:
            print(f"Unexpected result type: {result.type}")
    else:
        abort(f"Error: {tx_data}")


def invoke_and_output(function_name, parameters=[], sign_func=None):
    tx_hash, tx_data = invoke_contract_function(
        function_name, parameters, sign_func=sign_func
    )
    print("Output:")
    output_tx_data(tx_data)
    print("Horizon tx:")
    print(f"{state['horizon_url']}/transactions/{tx_hash}")
    print()
    print("Success!")


def issuer_as_bytes(asset_issuer: Optional[str]) -> Optional[Bytes]:
    if asset_issuer:
        return Bytes(asset_issuer.encode())
    else:
        return None


def build_asset_enum(asset_type: AssetType, asset: str):
    if asset_type == AssetType.stellar:
        return Enum("Stellar", Address(asset))
    elif asset_type == AssetType.other:
        return Enum("Other", Symbol(asset))
    else:
        return ValueError(f"unexpected asset_type: {asset_type}")


def gen_sign_func(signer_secret):
    def sign_f(tx):
        latest_ledger = state["soroban_server"].get_latest_ledger().sequence
        op = tx.transaction.operations[0]
        assert isinstance(op, InvokeHostFunction)
        authorization_entry: AuthorizationEntry = op.auth[0]
        authorization_entry.set_signature_expiration_ledger(latest_ledger + 3)
        authorization_entry.sign(signer_secret, state["network_passphrase"])

    return sign_f


@app.command(help="Deploy the contract to Stellar blockchain")
def deploy():
    contract_wasm_path = str(
        (
            Path(__file__).parent.parent
            / "contract"
            / "target"
            / "wasm32-unknown-unknown"
            / "release"
            / "oracle.wasm"
        ).resolve()
    )
    tx = (
        TransactionBuilder(state["source_acc"], state["network_passphrase"])
        .set_timeout(300)
        .append_upload_contract_wasm_op(
            contract=contract_wasm_path,  # the path to the contract, or binary data
        )
        .build()
    )

    tx = state["soroban_server"].prepare_transaction(tx)
    tx.sign(state["kp"])
    send_transaction_data = state["soroban_server"].send_transaction(tx)
    vprint(f"sent transaction: {send_transaction_data}")

    while True:
        vprint("waiting for transaction to be confirmed...")
        get_transaction_data = state["soroban_server"].get_transaction(
            send_transaction_data.hash
        )
        if get_transaction_data.status != GetTransactionStatus.NOT_FOUND:
            break
        time.sleep(3)

    vprint(f"transaction: {get_transaction_data}")

    wasm_id = None
    if get_transaction_data.status == GetTransactionStatus.SUCCESS:
        assert get_transaction_data.result_meta_xdr is not None
        transaction_meta = stellar_xdr.TransactionMeta.from_xdr(  # type: ignore
            get_transaction_data.result_meta_xdr
        )
        wasm_id = transaction_meta.v3.soroban_meta.return_value.bytes.sc_bytes.hex()  # type: ignore
        vprint(f"wasm id: {wasm_id}")

    assert wasm_id, "wasm id should not be empty"

    vprint("creating contract...")

    source = state["soroban_server"].load_account(
        state["kp"].public_key
    )  # refresh source account, because the current SDK will increment the sequence number by one after building a transaction

    tx = (
        TransactionBuilder(source, state["network_passphrase"])
        .set_timeout(300)
        .append_create_contract_op(
            wasm_id=wasm_id,
        )
        .build()
    )

    tx = state["soroban_server"].prepare_transaction(tx)
    tx.sign(state["kp"])

    send_transaction_data = state["soroban_server"].send_transaction(tx)
    vprint(f"sent transaction: {send_transaction_data}")

    while True:
        vprint("waiting for transaction to be confirmed...")
        get_transaction_data = state["soroban_server"].get_transaction(
            send_transaction_data.hash
        )
        if get_transaction_data.status != GetTransactionStatus.NOT_FOUND:
            break
        time.sleep(3)

    vprint(f"transaction: {get_transaction_data}")

    if get_transaction_data.status == GetTransactionStatus.SUCCESS:
        assert get_transaction_data.result_meta_xdr is not None
        transaction_meta = stellar_xdr.TransactionMeta.from_xdr(  # type: ignore
            get_transaction_data.result_meta_xdr
        )
        result = transaction_meta.v3.soroban_meta.return_value.address.contract_id.hash  # type: ignore
        contract_id = StrKey.encode_contract(result)
        vprint(f"contract id: {contract_id}")
        print(contract_id)


@app.command(help="Invoke the initialize() function of the contract")
def initialize(admin: str, base: str, decimals: int, resolution: int):
    func_name = "initialize"
    args = [
        Address(admin),
        build_asset_enum(AssetType.other, base),
        Uint32(decimals),
        Uint32(resolution),
    ]
    invoke_and_output(func_name, args, sign_func=gen_sign_func(state["kp"]))


@app.command(help="Invoke the admin() function of the contract")
def admin():
    invoke_and_output("admin")


@app.command(help="Invoke the base() function of the contract")
def base():
    invoke_and_output("base")


@app.command(help="Invoke the sources() function of the contract")
def sources():
    invoke_and_output("sources")


@app.command(help="Invoke the assets() function of the contract")
def assets():
    invoke_and_output("assets")


@app.command(help="Invoke the decimals() function of the contract")
def decimals():
    invoke_and_output("decimals")


@app.command(help="Invoke the resolution() function of the contract")
def resolution():
    invoke_and_output("resolution")


@app.command(help="Invoke the prices() function of the contract")
def prices(asset_type: AssetType, asset: str, start_timestamp: int, end_timestamp: int):
    invoke_and_output(
        "prices",
        [
            build_asset_enum(asset_type, asset),
            Uint64(start_timestamp),
            Uint64(end_timestamp),
        ],
    )


@app.command(help="Invoke the prices_by_source() function of the contract")
def prices_by_source(
    source: int,
    asset_type: AssetType,
    asset: str,
    start_timestamp: int,
    end_timestamp: int,
):
    invoke_and_output(
        "prices_by_source",
        [
            Uint32(source),
            build_asset_enum(asset_type, asset),
            Uint64(start_timestamp),
            Uint64(end_timestamp),
        ],
    )


@app.command(help="Invoke the lastprices() function of the contract")
def lastprices(
    asset_type: AssetType,
    asset: str,
    records: int,
):
    invoke_and_output(
        "lastprices",
        [
            build_asset_enum(asset_type, asset),
            Uint32(records),
        ],
    )


@app.command(help="Invoke the lastprices_by_source() function of the contract")
def lastprices_by_source(
    source: int,
    asset_type: AssetType,
    asset: str,
    records: int,
):
    invoke_and_output(
        "lastprices_by_source",
        [
            Uint32(source),
            build_asset_enum(asset_type, asset),
            Uint32(records),
        ],
    )


@app.command(help="Invoke the lastprice() function of the contract")
def lastprice(
    asset_type: AssetType,
    asset: str,
):
    invoke_and_output(
        "lastprice",
        [
            build_asset_enum(asset_type, asset),
        ],
    )


@app.command(help="Invoke the lastprice_by_source() function of the contract")
def lastprice_by_source(
    source: int,
    asset_type: AssetType,
    asset: str,
):
    invoke_and_output(
        "lastprice_by_source",
        [
            Uint32(source),
            build_asset_enum(asset_type, asset),
        ],
    )


@app.command(help="Invoke the add_price() function of the contract")
def add_price(source: int, asset_type: AssetType, asset: str, price: str):
    try:
        price_d = Decimal(price)
    except (TypeError, ValueError):
        abort("Invalid price")
        return
    price_d_str = "{:f}".format(price_d)
    price_parts = price_d_str.split(".")
    price_as_int = int(price_d_str.replace(".", ""))
    if len(price_parts) == 2:
        decimal_places = len(price_parts[1])
    else:
        decimal_places = 0
    zeroes_to_add = MAX_DECIMAL_PLACES - decimal_places
    if zeroes_to_add >= 0:
        price_as_int = price_as_int * (10**zeroes_to_add)
    else:
        abort(
            f"Invalid price: no more than {MAX_DECIMAL_PLACES} decimal places are allowed"
        )
        return
    func_name = "add_price"
    args = [
        Uint32(source),
        build_asset_enum(asset_type, asset),
        Int128(price_as_int),
    ]
    invoke_and_output(func_name, args, sign_func=gen_sign_func(state["kp"]))


@app.callback()
def main(
    verbose: bool = typer.Option(False, "-v", "--verbose"),
    contract_id: Optional[str] = typer.Option(None, "--contract-id"),
):
    if verbose:
        state["verbose"] = True
    if contract_id:
        state["contract_id"] = contract_id


if __name__ == "__main__":
    app()
