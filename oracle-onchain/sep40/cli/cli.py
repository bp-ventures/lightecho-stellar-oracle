#!/usr/bin/env -S poetry run python
from decimal import Decimal
import enum
import importlib.util
from pathlib import Path
import sys
import time
from typing import Optional

from colorama import init as colorama_init
from colorama import Fore
from colorama import Style
from stellar_sdk import (
    Keypair,
    StrKey,
    TransactionBuilder,
    TransactionEnvelope,
)
from stellar_sdk import xdr as stellar_xdr, scval
from stellar_sdk.soroban_server import SorobanServer
from stellar_sdk.soroban_rpc import GetTransactionStatus, SendTransactionStatus
from stellar_sdk.xdr.sc_val_type import SCValType
from stellar_sdk.exceptions import PrepareTransactionException
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
oracle_app = typer.Typer()
priceupdown_app = typer.Typer()
app = typer.Typer()
app.add_typer(oracle_app, name="oracle")
app.add_typer(priceupdown_app, name="priceupdown")

state = {
    "verbose": False,
    "source_secret": local_settings.SOURCE_SECRET,
    "admin_secret": local_settings.ADMIN_SECRET,
    "rpc_server_url": local_settings.RPC_SERVER_URL,
    "oracle_contract_id": local_settings.ORACLE_CONTRACT_ID,
    "priceupdown_contract_id": local_settings.PRICEUPDOWN_CONTRACT_ID,
    "network_passphrase": local_settings.NETWORK_PASSPHRASE,
    "horizon_url": "https://horizon-futurenet.stellar.org",
}
state["kp"] = Keypair.from_secret(state["source_secret"])
state["admin_kp"] = Keypair.from_secret(state["admin_secret"])
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


def send_tx(tx: TransactionEnvelope, signer=None):
    vprint(f"preparing transaction: {tx.to_xdr()}")
    try:
        tx = state["soroban_server"].prepare_transaction(tx)
    except PrepareTransactionException as e:
        print_error(str(getattr(e, "simulate_transaction_response", "")))
        raise e
    vprint(f"prepared transaction: {tx.to_xdr()}")

    if signer is not None:
        tx.sign(signer)
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


def invoke_contract_function(
    function_name, parameters=[], signer=None, contract_id=None
):
    if contract_id is None:
        contract_id = state["oracle_contract_id"]

    tx = (
        TransactionBuilder(
            state["source_acc"],
            state["network_passphrase"],
            base_fee=300000,
        )
        .set_timeout(30)
        .append_invoke_contract_function_op(
            contract_id,
            function_name,
            parameters,
        )
        .build()
    )

    tx_hash, tx_data = send_tx(tx, signer=signer)
    vprint(f"transaction: {tx_data}")

    if tx_data.status != GetTransactionStatus.SUCCESS:
        abort(f"Error: {tx_data}")

    return tx_hash, tx_data


def is_tx_success(tx_data):
    return tx_data.status == GetTransactionStatus.SUCCESS


def parse_tx_result(tx_data):
    assert tx_data.result_meta_xdr is not None
    transaction_meta = stellar_xdr.TransactionMeta.from_xdr(tx_data.result_meta_xdr)  # type: ignore
    # TODO handle multiple results[]
    assert transaction_meta.v3.soroban_meta
    result = transaction_meta.v3.soroban_meta.return_value
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


def output_tx_data(tx_data):
    vprint(f"transaction: {tx_data}")
    if is_tx_success(tx_data):
        result = parse_tx_result(tx_data)
        if result.type == SCValType.SCV_BOOL:
            print(result.b)
        elif result.type == SCValType.SCV_VOID:
            print("<void>")
        elif result.type == SCValType.SCV_MAP:
            assert result.map is not None
            print(parse_sc_map(result.map.sc_map))
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


def invoke_and_output(function_name, parameters=[], signer=None, contract_id=None):
    tx_hash, tx_data = invoke_contract_function(
        function_name, parameters, signer=signer, contract_id=contract_id
    )
    print("Output:")
    output_tx_data(tx_data)
    print("Horizon tx:")
    print(f"{state['horizon_url']}/transactions/{tx_hash}")
    print()
    print("Success!")


def issuer_as_bytes(asset_issuer: Optional[str]):
    if asset_issuer:
        return scval.to_bytes(asset_issuer.encode())
    else:
        return None


def build_asset_enum(asset_type: AssetType, asset: str):
    if asset_type == AssetType.stellar:
        return scval.to_enum("Stellar", scval.to_address(asset))
    elif asset_type == AssetType.other:
        return scval.to_enum("Other", scval.to_symbol(asset))
    else:
        return ValueError(f"unexpected asset_type: {asset_type}")


def deploy(contract_wasm_path: str):
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
            address=state["kp"].public_key,
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

@oracle_app.command("deploy", help="oracle: deploy contract")
def oracle_deploy():
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
    deploy(contract_wasm_path)


@oracle_app.command("initialize", help="oracle: invoke initialize()")
def oracle_initialize(admin: str, base: str, decimals: int, resolution: int):
    func_name = "initialize"
    args = [
        scval.to_address(admin),
        build_asset_enum(AssetType.other, base),
        scval.to_uint32(decimals),
        scval.to_uint32(resolution),
    ]
    invoke_and_output(func_name, args)


@oracle_app.command("has_admin", help="oracle: invoke has_admin()")
def oracle_has_admin():
    invoke_and_output("has_admin")


@oracle_app.command("write_admin", help="oracle: invoke write_admin()")
def oracle_write_admin():
    raise RuntimeError("This function is not yet available")


@oracle_app.command("read_admin", help="oracle: invoke read_admin()")
def oracle_read_admin():
    invoke_and_output("read_admin")


@oracle_app.command("sources", help="oracle: invoke sources()")
def oracle_sources():
    invoke_and_output("sources")


@oracle_app.command("prices_by_source", help="oracle: invoke prices_by_source()")
def oracle_prices_by_source(
    source: int,
    asset_type: AssetType,
    asset: str,
    records: int,
):
    invoke_and_output(
        "prices_by_source",
        [
            scval.to_uint32(source),
            build_asset_enum(asset_type, asset),
            scval.to_uint32(records),
        ],
    )


@oracle_app.command("price_by_source", help="oracle: invoke prices_by_source")
def oracle_price_by_source(
    source: int,
    asset_type: AssetType,
    asset: str,
    timestamp: int,
):
    invoke_and_output(
        "price_by_source",
        [
            scval.to_uint32(source),
            build_asset_enum(asset_type, asset),
            scval.to_uint32(timestamp),
        ],
    )


@oracle_app.command("lastprice_by_source", help="oracle: invoke lastprice_by_source")
def oracle_lastprice_by_source(
    source: int,
    asset_type: AssetType,
    asset: str,
):
    invoke_and_output(
        "lastprice_by_source",
        [
            scval.to_uint32(source),
            build_asset_enum(asset_type, asset),
        ],
    )


@oracle_app.command("add_price", help="oracle: invoke add_price()")
def oracle_add_price(
    source: int,
    asset_type: AssetType,
    asset: str,
    price: str,
    timestamp: Optional[int] = None,
):
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
    if timestamp is None:
        timestamp = int(time.time())
    func_name = "add_price"
    args = [
        scval.to_uint32(source),
        build_asset_enum(asset_type, asset),
        scval.to_int128(price_as_int),
        scval.to_uint64(timestamp),
    ]
    invoke_and_output(func_name, args, signer=state["admin_kp"])


@oracle_app.command("remove_prices", help="oracle: invoke remove_prices()")
def oracle_remove_prices():
    # TODO
    pass


@oracle_app.command("base", help="oracle: invoke base()")
def oracle_base():
    invoke_and_output("base")


@oracle_app.command("assets", help="oracle: invoke assets()")
def oracle_assets():
    invoke_and_output("assets")


@oracle_app.command("decimals", help="oracle: invoke decimals()")
def oracle_decimals():
    invoke_and_output("decimals")


@oracle_app.command("resolution", help="oracle: invoke resolution()")
def oracle_resolution():
    invoke_and_output("resolution")


@oracle_app.command("price", help="oracle: invoke price()")
def oracle_price(
    asset_type: AssetType,
    asset: str,
    timestamp: int,
):
    invoke_and_output(
        "price",
        [
            build_asset_enum(asset_type, asset),
            scval.to_uint64(timestamp),
        ],
    )


@oracle_app.command("prices", help="oracle: invoke prices()")
def oracle_prices(asset_type: AssetType, asset: str, records: int):
    invoke_and_output(
        "prices",
        [
            build_asset_enum(asset_type, asset),
            scval.to_uint32(records),
        ],
    )


@oracle_app.command("lastprice", help="oracle: invoke lastprice()")
def oracle_lastprice(
    asset_type: AssetType,
    asset: str,
):
    invoke_and_output(
        "lastprice",
        [
            build_asset_enum(asset_type, asset),
        ],
    )


@priceupdown_app.command("deploy", help="priceupdown: deploy contract")
def priceupdown_deploy():
    contract_wasm_path = str(
        (
            Path(__file__).parent.parent
            / "examples"
            / "price_up_down"
            / "target"
            / "wasm32-unknown-unknown"
            / "release"
            / "price_up_down.wasm"
        ).resolve()
    )
    deploy(contract_wasm_path)


@priceupdown_app.command("initialize", help="priceupdown: invoke initialize()")
def priceupdown_initialize(oracle_contract_id: str):
    invoke_and_output(
        "initialize",
        [
            scval.to_address(oracle_contract_id),
        ],
        contract_id=state["priceupdown_contract_id"],
    )


@priceupdown_app.command("lastprice", help="priceupdown: invoke lastprice()")
def priceupdown_lastprice(
    asset_type: AssetType,
    asset: str,
):
    invoke_and_output(
        "lastprice",
        [
            build_asset_enum(asset_type, asset),
        ],
        contract_id=state["priceupdown_contract_id"],
    )


@priceupdown_app.command(
    "get_price_up_down", help="priceupdown: invoke get_price_up_down()"
)
def priceupdown_get_price_up_down(
    asset_type: AssetType,
    asset: str,
):
    invoke_and_output(
        "get_price_up_down",
        [
            build_asset_enum(asset_type, asset),
        ],
        contract_id=state["priceupdown_contract_id"],
    )


@app.callback()
def main(
    verbose: bool = typer.Option(False, "-v", "--verbose"),
    oracle_contract_id: Optional[str] = typer.Option(None, "--oracle-contract-id"),
    priceupdown_contract_id: Optional[str] = typer.Option(
        None, "--priceupdown-contract-id"
    ),
):
    if verbose:
        state["verbose"] = True
    if oracle_contract_id:
        state["oracle_contract_id"] = oracle_contract_id
    if priceupdown_contract_id:
        state["priceupdown_contract_id"] = priceupdown_contract_id


if __name__ == "__main__":
    app()
