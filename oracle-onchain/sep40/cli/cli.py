import base64
import enum
import importlib.util
import json
from pathlib import Path
import sys
from typing import Optional

from colorama import init as colorama_init
from colorama import Fore
from colorama import Style
from lightecho_stellar_oracle import OracleClient
from stellar_sdk import Keypair
from stellar_sdk import scval
from stellar_sdk.soroban_server import SorobanServer
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
    "standalone": {
        "rpc_server_url": "http://localhost:8000/soroban/rpc",
        "network_passphrase": "Standalone Network ; February 2017",
        "horizon_url": "http://localhost:8000",
    },
}

colorama_init()
oracle_app = typer.Typer()
app = typer.Typer()
app.add_typer(oracle_app, name="oracle")

state = {
    "verbose": False,
    "source_secret": local_settings.SOURCE_SECRET,
    "admin_secret": local_settings.ADMIN_SECRET,
    "rpc_server_url": STELLAR_NETWORKS[local_settings.STELLAR_NETWORK][
        "rpc_server_url"
    ],
    "oracle_contract_id": local_settings.ORACLE_CONTRACT_ID,
    "network_passphrase": STELLAR_NETWORKS[local_settings.STELLAR_NETWORK][
        "network_passphrase"
    ],
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


def print_contract_output(tx_hash, tx_data):
    print("Output:")
    print(tx_data)
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


@oracle_app.command("initialize", help="oracle: invoke initialize()")
def oracle_initialize(admin: str, base: str, decimals: int, resolution: int):
    tx_hash, tx_data = state["oracle_client"].initialize(
        admin,
        "other",
        base,
        decimals,
        resolution,
    )
    print_contract_output(tx_hash, tx_data)


@oracle_app.command("bump_instance", help="oracle: invoke bump_instance()")
def oracle_bump_instance():
    tx_hash, tx_data = state["oracle_client"].bump_instance()
    print_contract_output(tx_hash, tx_data)


@oracle_app.command("has_admin", help="oracle: invoke has_admin()")
def oracle_has_admin():
    tx_hash, tx_data = state["oracle_client"].has_admin()
    print_contract_output(tx_hash, tx_data)


@oracle_app.command("write_admin", help="oracle: invoke write_admin()")
def oracle_write_admin():
    raise RuntimeError("This function is not yet available")


@oracle_app.command("read_admin", help="oracle: invoke read_admin()")
def oracle_read_admin():
    tx_hash, tx_data = state["oracle_client"].read_admin()
    print_contract_output(tx_hash, tx_data)


@oracle_app.command("sources", help="oracle: invoke sources()")
def oracle_sources():
    tx_hash, tx_data = state["oracle_client"].sources()
    print_contract_output(tx_hash, tx_data)


@oracle_app.command("prices_by_source", help="oracle: invoke prices_by_source()")
def oracle_prices_by_source(
    source: int,
    asset_type: AssetType,
    asset: str,
    records: int,
):
    tx_hash, tx_data = state["oracle_client"].prices_by_source(
        source,
        asset_type.name,
        asset,
        records,
    )
    print_contract_output(tx_hash, tx_data)


@oracle_app.command("price_by_source", help="oracle: invoke prices_by_source")
def oracle_price_by_source(
    source: int,
    asset_type: AssetType,
    asset: str,
    timestamp: int,
):
    tx_hash, tx_data = state["oracle_client"].price_by_source(
        source,
        asset_type.name,
        asset,
        timestamp,
    )
    print_contract_output(tx_hash, tx_data)


@oracle_app.command("lastprice_by_source", help="oracle: invoke lastprice_by_source")
def oracle_lastprice_by_source(
    source: int,
    asset_type: AssetType,
    asset: str,
):
    tx_hash, tx_data = state["oracle_client"].lastprice_by_source(
        source,
        asset_type.name,
        asset,
    )
    print_contract_output(tx_hash, tx_data)


@oracle_app.command("add_price", help="oracle: invoke add_price()")
def oracle_add_price(
    source: int,
    asset_type: AssetType,
    asset: str,
    price: str,
    timestamp: Optional[int] = None,
):
    tx_hash, tx_data = state["admin_oracle_client"].add_price(
        source,
        asset_type.name,
        asset,
        price,
        timestamp,
    )
    print_contract_output(tx_hash, tx_data)


@oracle_app.command("add_prices", help="oracle: invoke add_prices()")
def oracle_add_prices(
    prices_base64: str = typer.Argument(
        ..., help="A base64-encoded JSON list of prices."
    ),
):
    decoded_bytes = base64.b64decode(prices_base64)
    decoded_list = json.loads(decoded_bytes)
    tx_hash, tx_data = state["admin_oracle_client"].add_prices(decoded_list)
    print_contract_output(tx_hash, tx_data)


@oracle_app.command("remove_prices", help="oracle: invoke remove_prices()")
def oracle_remove_prices():
    # TODO
    pass


@oracle_app.command(
    "lastprices_by_source_and_assets",
    help="oracle: invoke lastprices_by_source_and_assets()",
)
def oracle_lastprices_by_source_and_assets(
    source: int,
    assets_base64: str = typer.Argument(
        ...,
        help="A base64-encoded JSON list. E.g. [{'asset_type': 'other', 'asset': 'BTC'}]. Note: fetching too many assets might result in errors from Soroban due to return size limits. We recommend requesting no more than 15 assets at a time.",
    ),
):
    assets = json.loads(base64.b64decode(assets_base64))
    if len(assets) > 15:
        print(
            "Warning: fetching too many assets at a time may result in errors.",
            file=sys.stderr,
        )
    tx_hash, tx_data = state["oracle_client"].lastprices_by_source_and_assets(
        source, assets
    )
    print_contract_output(tx_hash, tx_data)


@oracle_app.command("base", help="oracle: invoke base()")
def oracle_base():
    tx_hash, tx_data = state["oracle_client"].base()
    print_contract_output(tx_hash, tx_data)


@oracle_app.command("assets", help="oracle: invoke assets()")
def oracle_assets():
    tx_hash, tx_data = state["oracle_client"].assets()
    print_contract_output(tx_hash, tx_data)


@oracle_app.command("decimals", help="oracle: invoke decimals()")
def oracle_decimals():
    tx_hash, tx_data = state["oracle_client"].decimals()
    print_contract_output(tx_hash, tx_data)


@oracle_app.command("resolution", help="oracle: invoke resolution()")
def oracle_resolution():
    tx_hash, tx_data = state["oracle_client"].resolution()
    print_contract_output(tx_hash, tx_data)


@oracle_app.command("price", help="oracle: invoke price()")
def oracle_price(
    asset_type: AssetType,
    asset: str,
    timestamp: int,
):
    tx_hash, tx_data = state["oracle_client"].price(
        asset_type.name,
        asset,
        timestamp,
    )
    print_contract_output(tx_hash, tx_data)


@oracle_app.command("prices", help="oracle: invoke prices()")
def oracle_prices(asset_type: AssetType, asset: str, records: int):
    tx_hash, tx_data = state["oracle_client"].prices(
        asset_type.name,
        asset,
        records,
    )
    print_contract_output(tx_hash, tx_data)


@oracle_app.command("lastprice", help="oracle: invoke lastprice()")
def oracle_lastprice(
    asset_type: AssetType,
    asset: str,
):
    tx_hash, tx_data = state["oracle_client"].lastprice(
        asset_type.name,
        asset,
    )
    print_contract_output(tx_hash, tx_data)


@oracle_app.command("update_contract", help="oracle: invoke update_contract()")
def oracle_update_contract(
    wasm_file: str = typer.Argument(..., help="Path to WASM file")
):
    with open(wasm_file, "rb") as f:
        wasm_bytes = f.read()
    tx_hash, tx_data = state["admin_oracle_client"].update_contract(wasm_bytes)
    print_contract_output(tx_hash, tx_data)


@app.callback()
def main(
    verbose: bool = typer.Option(False, "-v", "--verbose"),
    oracle_contract_id: Optional[str] = typer.Option(None, "--oracle-contract-id"),
):
    if verbose:
        state["verbose"] = True
    if oracle_contract_id:
        state["oracle_contract_id"] = oracle_contract_id
    state["oracle_client"] = OracleClient(
        contract_id=state["oracle_contract_id"],
        signer=Keypair.from_secret(state["source_secret"]),
        network=local_settings.STELLAR_NETWORK,
    )
    state["admin_oracle_client"] = OracleClient(
        contract_id=state["oracle_contract_id"],
        signer=Keypair.from_secret(state["admin_secret"]),
        network=local_settings.STELLAR_NETWORK,
    )


if __name__ == "__main__":
    app()
