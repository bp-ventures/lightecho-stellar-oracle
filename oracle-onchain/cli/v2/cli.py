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
from stellar_sdk import Keypair, TransactionBuilder, TransactionEnvelope
from stellar_sdk import xdr as stellar_xdr
from stellar_sdk.soroban import AuthorizedInvocation, ContractAuth
from stellar_sdk.soroban.server import SorobanServer
from stellar_sdk.soroban.soroban_rpc import GetTransactionStatus, SendTransactionStatus
from stellar_sdk.soroban.types import (
    Address,
    Bytes,
    Enum,
    Symbol,
    Uint128,
    Uint32,
    Uint64,
    Int128,
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

colorama_init()
app = typer.Typer()
state = {
    "verbose": False,
    "source_secret": local_settings.SOURCE_SECRET,
    "rpc_server_url": local_settings.RPC_SERVER_URL,
    "contract_id": local_settings.CONTRACT_ID,
    "network_passphrase": local_settings.NETWORK_PASSPHRASE,
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


def send_tx(tx: TransactionEnvelope):
    vprint(f"preparing transaction: {tx.to_xdr()}")
    prepared_tx = state["soroban_server"].prepare_transaction(tx)
    vprint(f"prepared transaction: {prepared_tx.to_xdr()}")

    prepared_tx.sign(state["kp"])

    send_transaction_data = state["soroban_server"].send_transaction(prepared_tx)
    vprint(f"sent transaction: {send_transaction_data}")
    if send_transaction_data.status == SendTransactionStatus.ERROR:
        raise RuntimeError(f"Failed to send transaction: {send_transaction_data}")

    return wait_tx(send_transaction_data.hash)


def wait_tx(tx_hash: str):
    while True:
        vprint("waiting for transaction to be confirmed...")
        get_transaction_data = state["soroban_server"].get_transaction(tx_hash)
        if get_transaction_data.status != GetTransactionStatus.NOT_FOUND:
            break
        time.sleep(3)
    return get_transaction_data


def invoke_contract_function(function_name, parameters=[], auth=None):
    tx = (
        TransactionBuilder(state["source_acc"], state["network_passphrase"])
        .set_timeout(300)
        .append_invoke_contract_function_op(
            state["contract_id"],
            function_name,
            parameters,
            auth=auth,  # type: ignore
        )
        .build()
    )

    tx_data = send_tx(tx)
    vprint(f"transaction: {tx_data}")

    if tx_data.status == GetTransactionStatus.SUCCESS:
        vprint("Success")
    else:
        abort(f"Error: {tx_data}")

    return tx_data


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
            return
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


def invoke_and_output(function_name, parameters=[], auth=None):
    tx_data = invoke_contract_function(function_name, parameters, auth)
    output_tx_data(tx_data)


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


def build_contract_auth(contract_id, func_name, args, address=None, nounce=None):
    invocation = AuthorizedInvocation(
        contract_id=contract_id,
        function_name=func_name,
        args=args,
        sub_invocations=[],
    )
    contract_auth = ContractAuth(
        address=address,
        nonce=nounce,
        root_invocation=invocation,
    )
    return contract_auth


@app.command(help="Invoke the initialize() function of the contract")
def initialize(admin: str, base: str, decimals: int, resolution: int):
    invoke_and_output(
        "initialize",
        [
            Address(admin),
            build_asset_enum(AssetType.other, base),
            Uint32(decimals),
            Uint32(resolution),
        ],
    )


@app.command(help="Invoke the base() function of the contract")
def base():
    invoke_and_output("base")


@app.command(help="Invoke the admin() function of the contract")
def admin():
    invoke_and_output("admin")


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
def add_price(source: int, asset_type: AssetType, asset: str, price: int):
    func_name = "add_price"
    args = [
        Uint32(source),
        build_asset_enum(asset_type, asset),
        Int128(price),
    ]
    contract_auth = build_contract_auth(state["contract_id"], func_name, args)
    invoke_and_output(func_name, args, auth=[contract_auth])


@app.callback()
def main(verbose: bool = typer.Option(False, "-v", "--verbose")):
    if verbose:
        state["verbose"] = True


if __name__ == "__main__":
    app()
