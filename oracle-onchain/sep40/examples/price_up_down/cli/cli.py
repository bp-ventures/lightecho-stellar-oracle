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
from lightecho_stellar_oracle import OracleClient
import typer

mod_spec = importlib.util.spec_from_file_location(
    "local_settings", Path(__file__).resolve().parent / "local_settings.py"
)
assert mod_spec
local_settings = importlib.util.module_from_spec(mod_spec)
sys.modules["local_settings"] = local_settings
assert mod_spec.loader
mod_spec.loader.exec_module(local_settings)

STELLAR_NETWORKS = {
    "futurenet": {
        "rpc_server_url": "https://rpc-futurenet.stellar.org:443/",
        "network_passphrase": "Test SDF Future Network ; October 2022",
        "horizon_url": "https://horizon-futurenet.stellar.org",
    },
    "testnet": {
        "rpc_server_url": "https://soroban-testnet.stellar.org",
        "network_passphrase": "Test SDF Network ; September 2015",
        "horizon_url": "https://horizon-testnet.stellar.org",
    },
}

colorama_init()
priceupdown_app = typer.Typer()
app = typer.Typer()
app.add_typer(priceupdown_app, name="priceupdown")

oracle_client = OracleClient(
    contract_id=local_settings.ORACLE_CONTRACT_ID,
    signer=Keypair.from_secret(local_settings.SOURCE_SECRET),
    network=local_settings.STELLAR_NETWORK,
)

state = {
    "verbose": False,
    "source_secret": local_settings.SOURCE_SECRET,
    "admin_secret": local_settings.ADMIN_SECRET,
    "rpc_server_url": STELLAR_NETWORKS[local_settings.STELLAR_NETWORK]["rpc_server_url"],
    "oracle_contract_id": local_settings.ORACLE_CONTRACT_ID,
    "priceupdown_contract_id": local_settings.PRICEUPDOWN_CONTRACT_ID,
    "network_passphrase": STELLAR_NETWORKS[local_settings.STELLAR_NETWORK]["network_passphrase"],
    "horizon_url": STELLAR_NETWORKS[local_settings.STELLAR_NETWORK]["horizon_url"],
}
state["kp"] = Keypair.from_secret(state["source_secret"])
state["admin_kp"] = Keypair.from_secret(state["admin_secret"])
state["soroban_server"] = SorobanServer(state["rpc_server_url"])
state["source_acc"] = state["soroban_server"].load_account(state["kp"].public_key)
state["admin_source_acc"] = state["soroban_server"].load_account(
    state["admin_kp"].public_key
)


class AssetType(enum.Enum):
    stellar = "stellar"
    other = "other"


def print_error(msg: str):
    print(Fore.RED + msg + Style.RESET_ALL)


def abort(msg: str):
    print_error(msg)
    raise typer.Exit(1)


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
    else:
        tx.sign(state["kp"])
    vprint(f"signed xdr: {tx.to_xdr()}")

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
    function_name, parameters=[], source_acc=None, signer=None, contract_id=None
):
    if contract_id is None:
        contract_id = state["priceupdown_contract_id"]
    if source_acc is None:
        source_acc = state["source_acc"]

    tx = (
        TransactionBuilder(
            source_acc,
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
            print(oracle_client.parse_sc_map(result.map.sc_map))
        elif result.type in [
            SCValType.SCV_U32,
            SCValType.SCV_I32,
            SCValType.SCV_U64,
            SCValType.SCV_I64,
            SCValType.SCV_U128,
            SCValType.SCV_I128,
            SCValType.SCV_SYMBOL,
        ]:
            print(oracle_client.parse_sc_val(result))
        elif result.type == SCValType.SCV_ADDRESS:
            print(str(result.address))
        elif result.type == SCValType.SCV_VEC:
            print(oracle_client.parse_sc_vec(result.vec))
        else:
            print(f"Unexpected result type: {result.type}")
    else:
        abort(f"Error: {tx_data}")


def invoke_and_output(
    function_name, parameters=[], source_acc=None, signer=None, contract_id=None
):
    tx_hash, tx_data = invoke_contract_function(
        function_name,
        parameters,
        source_acc=source_acc,
        signer=signer,
        contract_id=contract_id,
    )
    print("Output:")
    output_tx_data(tx_data)
    print("Horizon tx:")
    print(f"{state['horizon_url']}/transactions/{tx_hash}")
    print()
    print("Success!")


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
def priceupdown_initialize():
    invoke_and_output(
        "initialize",
        [
            scval.to_address(state["oracle_contract_id"]),
        ],
        contract_id=state["priceupdown_contract_id"],
    )


@priceupdown_app.command("bump_instance", help="priceupdown: invoke bump_instance()")
def priceupdown_bump_instance():
    invoke_and_output(
        "bump_instance",
        [],
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
):
    if verbose:
        state["verbose"] = True


if __name__ == "__main__":
    app()
