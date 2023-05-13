#!/usr/bin/env -S poetry run python
from decimal import Decimal
import json
import time
from typing import Optional
from pathlib import Path

from colorama import init as colorama_init
from colorama import Fore
from colorama import Style
from stellar_sdk import Keypair, Network, TransactionBuilder, TransactionEnvelope
from stellar_sdk import xdr as stellar_xdr
from stellar_sdk.soroban.server import SorobanServer
from stellar_sdk.soroban.soroban_rpc import GetTransactionStatus
from stellar_sdk.soroban.types import Bytes, Symbol, Uint128, Uint64
import typer

import importlib.util
import sys

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


def print_error(msg: str):
    print(Fore.RED + msg + Style.RESET_ALL)


def abort(msg: str):
    print_error(msg)
    raise typer.Exit()


def send_tx(tx: TransactionEnvelope):
    simulate_transaction_data = state["soroban_server"].simulate_transaction(tx)
    if state["verbose"]:
        print(f"simulated transaction: {simulate_transaction_data}")
    if simulate_transaction_data.error:
        raise RuntimeError("simulated transaction failed")

    if state["verbose"]:
        print(f"setting footprint and signing transaction...")
    assert simulate_transaction_data.results is not None
    tx.set_footpoint(simulate_transaction_data.results[0].footprint)
    tx.sign(state["kp"])

    send_transaction_data = state["soroban_server"].send_transaction(tx)
    if state["verbose"]:
        print(f"sent transaction: {send_transaction_data}")

    return wait_tx(send_transaction_data.hash)


def wait_tx(tx_hash: str):
    while True:
        if state["verbose"]:
            print("waiting for transaction to be confirmed...")
        get_transaction_data = state["soroban_server"].get_transaction(tx_hash)
        if get_transaction_data.status != GetTransactionStatus.NOT_FOUND:
            break
        time.sleep(3)
    return get_transaction_data


def invoke_contract_function(function_name, parameters=[]):
    tx = (
        TransactionBuilder(state["source_acc"], state["network_passphrase"])
        .set_timeout(300)
        .append_invoke_contract_function_op(
            state["contract_id"],
            function_name,
            parameters,
            source=state["kp"].public_key,
        )
        .build()
    )

    tx_data = send_tx(tx)
    if state["verbose"]:
        print(f"transaction: {tx_data}")

    if state["verbose"]:
        if tx_data.status == GetTransactionStatus.SUCCESS:
            print("Success")
        else:
            abort(f"Error: {tx_data}")

    return tx_data


def is_tx_success(tx_data):
    return tx_data.status == GetTransactionStatus.SUCCESS


def parse_tx_result(tx_data):
    assert tx_data.result_meta_xdr is not None
    transaction_meta = stellar_xdr.TransactionMeta.from_xdr(tx_data.result_meta_xdr)
    result = transaction_meta.v3.tx_result.result.results[0].tr.invoke_host_function_result.success  # type: ignore
    return result


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


def output_tx_data(tx_data):
    if state["verbose"]:
        print(f"transaction: {tx_data}")
    if is_tx_success(tx_data):
        result = parse_tx_result(tx_data)
        if result.map:
            data = {}
            for entry in result.map.sc_map:
                key = entry.key.sym.sc_symbol.decode()
                value = parse_sc_val(entry.val)
                data[key] = value
            print(json.dumps(data, indent=2))
        elif result.sym:
            print(result.sym.sc_symbol.decode())
        else:
            return
    else:
        abort(f"Error: {tx_data}")


def invoke_and_output(function_name, parameters=[]):
    tx_data = invoke_contract_function(function_name, parameters)
    output_tx_data(tx_data)


def issuer_as_bytes(asset_issuer: Optional[str]) -> Optional[Bytes]:
    if asset_issuer:
        return Bytes(asset_issuer.encode())
    else:
        return None


@app.command(help="Invoke the get_base() function of the contract")
def get_base():
    invoke_and_output("get_base")


@app.command(help="Invoke the get_rate() function of the contract")
def get_rate(asset_code: str, asset_issuer: str, source: int):
    invoke_and_output(
        "get_rate", [Symbol(asset_code), issuer_as_bytes(asset_issuer), Uint64(source)]
    )


@app.command(help="Invoke the set_base() function of the contract")
def set_base(base: str):
    invoke_and_output("set_base", [Symbol(base)])


@app.command(help="Invoke the set_rate() function of the contract")
def set_rate(
    asset_code: str,
    asset_issuer: Optional[str],
    source: int,
    rate: str,
    decimals: Optional[int] = None,
    timestamp: Optional[int] = None,
):
    if timestamp is None:
        timestamp = int(time.time())
    try:
        rate_d = Decimal(rate)
    except (TypeError, ValueError):
        abort("Invalid price")
        return
    rate_d_str = "{:f}".format(rate_d)
    rate_parts = rate_d_str.split(".")
    rate_as_int = int(rate_d_str.replace(".", ""))
    if len(rate_parts) > 1:
        if decimals is not None:
            abort("decimals can only be provided alongside an integer price")
            return
        decimal_places = len(rate_parts[1])
    else:
        if decimals is not None:
            decimal_places = decimals
        else:
            decimal_places = 0
    invoke_and_output(
        "set_rate",
        [
            Symbol(asset_code),
            issuer_as_bytes(asset_issuer),
            Uint64(source),
            Uint128(rate_as_int),
            Uint128(decimal_places),
            Uint64(timestamp),
        ],
    )


@app.callback()
def main(verbose: bool = typer.Option(False, "-v", "--verbose")):
    if verbose:
        state["verbose"] = True


if __name__ == "__main__":
    app()
