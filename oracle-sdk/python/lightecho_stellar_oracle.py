from decimal import Decimal
import time
from typing import Optional, Literal

from stellar_sdk import (
    Keypair,
    StrKey,
    TransactionBuilder,
    TransactionEnvelope,
    Network as SdkNetwork,
)
from stellar_sdk import scval, xdr as stellar_xdr
from stellar_sdk.soroban_rpc import GetTransactionStatus, SendTransactionStatus
from stellar_sdk.soroban_server import SorobanServer
from stellar_sdk.xdr.sc_val_type import SCValType


AssetType = Literal["stellar", "other"]
Network = Literal["futurenet", "testnet", "public"]


class OracleClient:
    def __init__(
        self,
        *,
        contract_id: str,
        signer: Keypair,
        network: Network,
        wait_tx_interval: int = 3,
        tx_timeout: int = 30,
        decimal_places: int = 18,
    ):
        if network == "futurenet":
            self.network_passphrase = SdkNetwork.FUTURENET_NETWORK_PASSPHRASE
            self.rpc_server_url = "https://rpc-futurenet.stellar.org:443/"
        elif network == "testnet":
            self.network_passphrase = SdkNetwork.TESTNET_NETWORK_PASSPHRASE
            self.rpc_server_url = "https://rpc-testnet.stellar.org:443/"
        elif network == "public":
            self.network_passphrase = SdkNetwork.PUBLIC_NETWORK_PASSPHRASE
            self.rpc_server_url = "https://rpc.stellar.org:443/"
        self.server = SorobanServer(self.rpc_server_url)
        self.contract_id = contract_id
        self.signer = signer
        self.wait_tx_interval = wait_tx_interval
        self.tx_timeout = tx_timeout
        self.decimal_places = decimal_places

    def build_asset_enum(self, asset_type: AssetType, asset: str):
        if asset_type == "stellar":
            return scval.to_enum("Stellar", scval.to_address(asset))
        elif asset_type == "other":
            return scval.to_enum("Other", scval.to_symbol(asset))
        else:
            return ValueError(f"unexpected asset_type: {asset_type}")

    def _send_tx(self, tx: TransactionEnvelope):
        tx = self.server.prepare_transaction(tx)
        tx.sign(self.signer)
        send_transaction_data = self.server.send_transaction(tx)
        if send_transaction_data.status != SendTransactionStatus.PENDING:
            raise RuntimeError(f"Failed to send transaction: {send_transaction_data}")
        tx_hash = send_transaction_data.hash
        return tx_hash, self._wait_tx(tx_hash)

    def _wait_tx(self, tx_hash: str):
        while True:
            get_transaction_data = self.server.get_transaction(tx_hash)
            if get_transaction_data.status != GetTransactionStatus.NOT_FOUND:
                break
            time.sleep(self.wait_tx_interval)
        return get_transaction_data

    def _invoke_contract_function(self, function_name, parameters=[]):
        source_account = self.server.load_account(self.signer.public_key)
        tx = (
            TransactionBuilder(
                source_account,
                self.network_passphrase,
                base_fee=300000,
            )
            .set_timeout(self.tx_timeout)
            .append_invoke_contract_function_op(
                self.contract_id,
                function_name,
                parameters,
            )
            .build()
        )

        tx_hash, tx_data = self._send_tx(tx)
        if tx_data.status != GetTransactionStatus.SUCCESS:
            raise RuntimeError(f"Failed to send transaction: {tx_data}")

        return tx_hash, tx_data

    def _is_tx_success(self, tx_data):
        return tx_data.status == GetTransactionStatus.SUCCESS

    def _parse_tx_result(self, tx_data):
        assert tx_data.result_meta_xdr is not None
        transaction_meta = stellar_xdr.TransactionMeta.from_xdr(tx_data.result_meta_xdr)  # type: ignore
        # TODO handle multiple results[]
        assert transaction_meta.v3.soroban_meta
        result = transaction_meta.v3.soroban_meta.return_value
        return result

    def _parse_sc_val(self, sc_val):
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
            return self._parse_sc_map(sc_val.map.sc_map)
        if sc_val.vec is not None:
            return self._parse_sc_vec(sc_val.vec)
        if sc_val.sym is not None:
            return sc_val.sym.sc_symbol.decode()
        raise ValueError("Could not parse sc_val")

    def _parse_sc_vec(self, sc_vec):
        vec = []
        for val in sc_vec.sc_vec:
            vec.append(self._parse_sc_val(val))
        return vec

    def _parse_sc_map(self, sc_map):
        data = {}
        for entry in sc_map:
            key = entry.key.sym.sc_symbol.decode()
            value = self._parse_sc_val(entry.val)
            data[key] = value
        return data

    def _parse_tx_data(self, tx_data):
        if self._is_tx_success(tx_data):
            result = self._parse_tx_result(tx_data)
            if result.type == SCValType.SCV_BOOL:
                return result.b
            elif result.type == SCValType.SCV_VOID:
                return
            elif result.type == SCValType.SCV_MAP:
                assert result.map is not None
                return self._parse_sc_map(result.map.sc_map)
            elif result.type in [
                SCValType.SCV_U32,
                SCValType.SCV_I32,
                SCValType.SCV_U64,
                SCValType.SCV_I64,
                SCValType.SCV_U128,
                SCValType.SCV_I128,
                SCValType.SCV_SYMBOL,
            ]:
                return self._parse_sc_val(result)
            elif result.type == SCValType.SCV_ADDRESS:
                return str(result.address)
            elif result.type == SCValType.SCV_VEC:
                return self._parse_sc_vec(result.vec)
            else:
                print(f"Unexpected result type: {result.type}")
        else:
            raise RuntimeError(f"Cannot parse unsuccessful transaction data: {tx_data}")

    def _invoke_and_parse(self, function_name, parameters=[]):
        tx_hash, tx_data = self._invoke_contract_function(
            function_name,
            parameters,
        )
        return tx_hash, self._parse_tx_data(tx_data)

    def _issuer_as_bytes(self, asset_issuer: Optional[str]):
        if asset_issuer:
            return scval.to_bytes(asset_issuer.encode())
        else:
            return None

    def initialize(
        self,
        admin: str,
        base_type: AssetType,
        base: str,
        decimals: int,
        resolution: int,
    ):
        return self._invoke_and_parse(
            "initialize",
            [
                scval.to_address(admin),
                self.build_asset_enum(base_type, base),
                scval.to_uint32(decimals),
                scval.to_uint32(resolution),
            ],
        )

    def has_admin(self):
        return self._invoke_and_parse("has_admin")

    def write_admin(self):
        raise RuntimeError("This function is not yet available")

    def read_admin(self):
        return self._invoke_and_parse("read_admin")

    def sources(self):
        return self._invoke_and_parse("sources")

    def prices_by_source(
        self, source: int, asset_type: AssetType, asset: str, records: int
    ):
        return self._invoke_and_parse(
            "prices_by_source",
            [
                scval.to_uint32(source),
                self.build_asset_enum(asset_type, asset),
                scval.to_uint32(records),
            ],
        )

    def price_by_source(
        self, source: int, asset_type: AssetType, asset: str, timestamp: int
    ):
        return self._invoke_and_parse(
            "price_by_source",
            [
                scval.to_uint32(source),
                self.build_asset_enum(asset_type, asset),
                scval.to_uint32(timestamp),
            ],
        )

    def lastprice_by_source(self, source: int, asset_type: AssetType, asset: str):
        return self._invoke_and_parse(
            "lastprice_by_source",
            [
                scval.to_uint32(source),
                self.build_asset_enum(asset_type, asset),
            ],
        )

    def add_price(
        self,
        source: int,
        asset_type: AssetType,
        asset: str,
        price: str,
        timestamp: Optional[int] = None,
    ):
        price_d = Decimal(price)
        price_d_str = "{:f}".format(price_d)
        price_parts = price_d_str.split(".")
        price_as_int = int(price_d_str.replace(".", ""))
        if len(price_parts) == 2:
            decimal_places = len(price_parts[1])
        else:
            decimal_places = 0
        zeroes_to_add = self.decimal_places - decimal_places
        if zeroes_to_add >= 0:
            price_as_int = price_as_int * (10**zeroes_to_add)
        else:
            raise ValueError(
                f"Invalid price: no more than {self.decimal_places} decimal places are allowed"
            )
        if timestamp is None:
            timestamp = int(time.time())
        func_name = "add_price"
        args = [
            scval.to_uint32(source),
            self.build_asset_enum(asset_type, asset),
            scval.to_int128(price_as_int),
            scval.to_uint64(timestamp),
        ]
        return self._invoke_and_parse(func_name, args)

    def remove_prices(self):
        raise RuntimeError("This function is not yet available")

    def base(self):
        return self._invoke_and_parse("base")

    def assets(self):
        return self._invoke_and_parse("assets")

    def decimals(self):
        return self._invoke_and_parse("decimals")

    def resolution(self):
        return self._invoke_and_parse("resolution")

    def price(
        self,
        asset_type: AssetType,
        asset: str,
        timestamp: int,
    ):
        return self._invoke_and_parse(
            "price",
            [
                self.build_asset_enum(asset_type, asset),
                scval.to_uint64(timestamp),
            ],
        )

    def prices(self, asset_type: AssetType, asset: str, records: int):
        return self._invoke_and_parse(
            "prices",
            [
                self.build_asset_enum(asset_type, asset),
                scval.to_uint32(records),
            ],
        )

    def lastprice(
        self,
        asset_type: AssetType,
        asset: str,
    ):
        return self._invoke_and_parse(
            "lastprice",
            [
                self.build_asset_enum(asset_type, asset),
            ],
        )


class OracleDeployer:
    def __init__(
        self,
        *,
        signer: Keypair,
        network: Network,
        wait_tx_interval: int = 3,
        tx_timeout: int = 30,
    ):
        if network == "futurenet":
            self.network_passphrase = SdkNetwork.FUTURENET_NETWORK_PASSPHRASE
            self.rpc_server_url = "https://rpc-futurenet.stellar.org:443/"
        elif network == "testnet":
            self.network_passphrase = SdkNetwork.TESTNET_NETWORK_PASSPHRASE
            self.rpc_server_url = "https://rpc-testnet.stellar.org:443/"
        elif network == "public":
            self.network_passphrase = SdkNetwork.PUBLIC_NETWORK_PASSPHRASE
            self.rpc_server_url = "https://rpc.stellar.org:443/"
        self.server = SorobanServer(self.rpc_server_url)
        self.signer = signer
        self.wait_tx_interval = wait_tx_interval
        self.tx_timeout = tx_timeout

    def deploy(self, contract_wasm_path: str):
        source_account = self.server.load_account(self.signer.public_key)
        tx = (
            TransactionBuilder(source_account, self.network_passphrase)
            .set_timeout(self.tx_timeout)
            .append_upload_contract_wasm_op(
                contract=contract_wasm_path,  # the path to the contract, or binary data
            )
            .build()
        )

        tx = self.server.prepare_transaction(tx)
        tx.sign(self.signer)
        send_transaction_data = self.server.send_transaction(tx)

        while True:
            get_transaction_data = self.server.get_transaction(
                send_transaction_data.hash
            )
            if get_transaction_data.status != GetTransactionStatus.NOT_FOUND:
                break
            time.sleep(self.wait_tx_interval)

        wasm_id = None
        if get_transaction_data.status == GetTransactionStatus.SUCCESS:
            assert get_transaction_data.result_meta_xdr is not None
            transaction_meta = stellar_xdr.TransactionMeta.from_xdr(  # type: ignore
                get_transaction_data.result_meta_xdr
            )
            wasm_id = transaction_meta.v3.soroban_meta.return_value.bytes.sc_bytes.hex()  # type: ignore

        if wasm_id is None:
            raise ValueError("wasm_id should not be empty")

        source_account = self.server.load_account(self.signer.public_key)

        tx = (
            TransactionBuilder(source_account, self.network_passphrase)
            .set_timeout(300)
            .append_create_contract_op(
                wasm_id=wasm_id,
                address=self.signer.public_key,
            )
            .build()
        )

        tx = self.server.prepare_transaction(tx)
        tx.sign(self.signer)

        send_transaction_data = self.server.send_transaction(tx)

        while True:
            get_transaction_data = self.server.get_transaction(
                send_transaction_data.hash
            )
            if get_transaction_data.status != GetTransactionStatus.NOT_FOUND:
                break
            time.sleep(self.wait_tx_interval)

        if get_transaction_data.status == GetTransactionStatus.SUCCESS:
            assert get_transaction_data.result_meta_xdr is not None
            transaction_meta = stellar_xdr.TransactionMeta.from_xdr(  # type: ignore
                get_transaction_data.result_meta_xdr
            )
            result = transaction_meta.v3.soroban_meta.return_value.address.contract_id.hash  # type: ignore
            contract_id = StrKey.encode_contract(result)
            return contract_id
        else:
            raise RuntimeError(f"Failed to send transaction: {get_transaction_data}")
