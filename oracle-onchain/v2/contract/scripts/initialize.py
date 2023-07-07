import enum
import os
import sys
import time

from colorama import init as colorama_init
from colorama import Fore
from colorama import Style
from stellar_sdk import Keypair, StrKey, TransactionBuilder, TransactionEnvelope
from stellar_sdk.exceptions import Ed25519SecretSeedInvalidError
from stellar_sdk.soroban.server import SorobanServer
from stellar_sdk.soroban.soroban_rpc import GetTransactionStatus, SendTransactionStatus
from stellar_sdk.soroban.types import Address, Enum as SorobanEnum, Symbol, Uint32
import typer

colorama_init()

def eprint(msg: str):
    print(Fore.RED + msg + Style.RESET_ALL)

state = {
    "rpc_server_url": "https://rpc-futurenet.stellar.org:443/",
    "network_passphrase": "Test SDF Future Network ; October 2022",
    "horizon_url": "https://horizon-futurenet.stellar.org",
}
server = SorobanServer(state["rpc_server_url"])
source_secret = os.getenv("SOURCE_SECRET", "")
try:
    source_kp = Keypair.from_secret(source_secret)
except Ed25519SecretSeedInvalidError:
    eprint("Invalid source secret from stdin")
    sys.exit(1)


class AssetType(enum.Enum):
    stellar = "stellar"
    other = "other"


def build_asset_enum(asset_type: AssetType, asset: str):
    if asset_type == AssetType.stellar:
        return SorobanEnum("Stellar", Address(asset))
    elif asset_type == AssetType.other:
        return SorobanEnum("Other", Symbol(asset))
    else:
        return ValueError(f"unexpected asset_type: {asset_type}")


def wait_tx(tx_hash: str):
    while True:
        print("Waiting for tx to be confirmed")
        get_transaction_data = server.get_transaction(tx_hash)
        if get_transaction_data.status != GetTransactionStatus.NOT_FOUND:
            break
        time.sleep(3)
    return get_transaction_data


def send_tx(tx: TransactionEnvelope):
    prepared_tx = server.prepare_transaction(tx)
    prepared_tx.sign(source_kp)

    send_transaction_data = server.send_transaction(prepared_tx)
    if send_transaction_data.status != SendTransactionStatus.PENDING:
        raise RuntimeError(f"Failed to send transaction: {send_transaction_data}")

    tx_hash = send_transaction_data.hash
    return tx_hash, wait_tx(tx_hash)


def initialize(contract_id: str, admin: str, base: str, decimals: int, resolution: int):
    source_acc = server.load_account(source_kp.public_key)
    contract_id = StrKey.decode_contract(contract_id).hex()
    tx = (
        TransactionBuilder(
            source_acc,
            state["network_passphrase"],
            base_fee=300000,
        )
        .set_timeout(30)
        .append_invoke_contract_function_op(
            contract_id,
            "initialize",
            [
                Address(admin),
                build_asset_enum(AssetType.other, base),  # type: ignore
                Uint32(decimals),
                Uint32(resolution),
            ],
        )
        .build()
    )

    tx_hash, tx_data = send_tx(tx)

    if tx_data.status != GetTransactionStatus.SUCCESS:
        eprint(f"Error: {tx_data}")
        sys.exit(1)

    print(f"Success! Tx: {state['horizon_url']}/transactions/{tx_hash}")


if __name__ == "__main__":
    typer.run(initialize)
