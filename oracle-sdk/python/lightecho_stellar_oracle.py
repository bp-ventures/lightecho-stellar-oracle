from decimal import Decimal
import logging
import time
from typing import List, Literal, Optional, Tuple, TypedDict, Union, Dict
import sys

from stellar_sdk import (
    Keypair,
    Network as StellarSdkNetwork,
    StrKey,
    TransactionBuilder,
    TransactionEnvelope,
    Address,
)
from stellar_sdk import scval, xdr as stellar_xdr
from stellar_sdk.exceptions import PrepareTransactionException
from stellar_sdk.soroban_rpc import GetTransactionStatus, SendTransactionStatus
from stellar_sdk.soroban_server import SorobanServer
from stellar_sdk.xdr.sc_val_type import SCValType


AssetType = Literal["stellar", "other"]
Network = Literal["standalone", "futurenet", "testnet", "public", "custom"]

TESTNET_CONTRACT_XLM = "CA335SIV2XT6OC3SOUTZBHTX5IXMFO3WYBD3NNVBP37JXX4FXFNF5CI6"
TESTNET_CONTRACT_USD = ""  # not deployed yet

DECIMAL_PLACES_DIVIDER = Decimal(10**18)
ASSETS_TO_ASSET_U32: Dict[Tuple, int] = {
    ("other", "ARST"): 0,
    ("other", "AUDD"): 1,
    ("other", "BRL"): 2,
    ("other", "BTC"): 3,
    ("other", "BTCLN"): 4,
    ("other", "CLPX"): 5,
    ("other", "ETH"): 6,
    ("other", "EUR"): 7,
    ("other", "EURC"): 8,
    ("other", "EURT"): 9,
    ("other", "GYEN"): 10,
    ("other", "IDRT"): 11,
    ("other", "KES"): 12,
    ("other", "KRW"): 13,
    ("other", "NGNT"): 14,
    ("other", "TRY"): 15,
    ("other", "TRYB"): 16,
    ("other", "TZS"): 17,
    ("other", "UPUSDT"): 18,
    ("other", "USD"): 19,
    ("other", "USDC"): 20,
    ("other", "USDT"): 21,
    ("other", "VOL30d"): 22,
    ("other", "XCHF"): 23,
    ("other", "XLM"): 24,
    ("other", "XSGD"): 25,
    ("other", "YUSDC"): 26,
    ("other", "ZAR"): 27,
    ("other", "yBTC"): 28,
    ("other", "yUSDC"): 29,
}


class AssetU32NotFound(Exception):
    pass


class Price(TypedDict):
    price: str
    timestamp: int


class AssetPrice(TypedDict):
    source: int
    asset_type: AssetType
    asset: str
    price: str
    timestamp: Optional[int]


class Asset(TypedDict):
    asset_type: AssetType
    asset: str


class OracleClient:
    def __init__(
        self,
        *,
        contract_id: str,
        signer: Keypair,
        network: Network,
        custom_rpc_url: Optional[str] = None,
        custom_network_passphrase: Optional[str] = None,
        wait_tx_interval: int = 3,
        tx_timeout: int = 30,
        decimal_places: int = 18,
    ):
        """
        Initializes an Oracle Client instance.

        Args:
            contract_id (str): The contract ID.
            signer (Keypair): The keypair used to sign transactions.
            network (Network): The Stellar network to connect to (e.g., "standalone", "futurenet", "testnet", "public").
            custom_rpc_url (str, optional): The custom RPC server URL. Default is None.
            custom_network_passphrase (str, optional): The custom network passphrase. Default is None.
            wait_tx_interval (int, optional): The interval to wait for a transaction (in seconds). Default is 3 seconds.
            tx_timeout (int, optional): The transaction timeout (in seconds). Default is 30 seconds.
            decimal_places (int, optional): The number of decimal places for prices. Default is 18.

        Returns:
            None
        """
        self.network = network
        if network == "standalone":
            self.network_passphrase = StellarSdkNetwork.STANDALONE_NETWORK_PASSPHRASE
            self.rpc_server_url = "http://localhost:8000/soroban/rpc"
        elif network == "futurenet":
            self.network_passphrase = StellarSdkNetwork.FUTURENET_NETWORK_PASSPHRASE
            self.rpc_server_url = "https://rpc-futurenet.stellar.org:443/"
        elif network == "testnet":
            self.network_passphrase = StellarSdkNetwork.TESTNET_NETWORK_PASSPHRASE
            self.rpc_server_url = "https://soroban-testnet.stellar.org:443/"
        elif network == "public":
            self.network_passphrase = StellarSdkNetwork.PUBLIC_NETWORK_PASSPHRASE
            self.rpc_server_url = "https://rpc.stellar.org:443/"
        elif network == "custom":
            if custom_rpc_url is None:
                raise ValueError("custom_rpc_url is required for custom network")
            if custom_network_passphrase is None:
                raise ValueError(
                    "custom_network_passphrase is required for custom network"
                )
            self.network_passphrase = custom_network_passphrase
            self.rpc_server_url = custom_rpc_url
        if network != "custom" and custom_rpc_url is not None:
            raise ValueError("custom_rpc_url is only allowed for custom network")
        if network != "custom" and custom_network_passphrase is not None:
            raise ValueError(
                "custom_network_passphrase is only allowed for custom network"
            )
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

    def send_tx(self, tx: TransactionEnvelope):
        """
        Sends a transaction and waits for confirmation.

        Args:
            tx (TransactionEnvelope): The transaction to send.

        Returns:
            Tuple[str, GetTransactionStatus]: A tuple containing the transaction hash and its status.
        """
        tx = self.server.prepare_transaction(tx)
        tx.sign(self.signer)
        send_transaction_data = self.server.send_transaction(tx)
        if send_transaction_data.status != SendTransactionStatus.PENDING:
            raise RuntimeError(f"Failed to send transaction: {send_transaction_data}")
        tx_hash = send_transaction_data.hash
        return tx_hash, self.wait_tx(tx_hash)

    def wait_tx(self, tx_hash: str):
        """
        Waits for a transaction to be confirmed.

        Args:
            tx_hash (str): The transaction hash.

        Returns:
            GetTransactionStatus: The status of the transaction.
        """
        while True:
            get_transaction_data = self.server.get_transaction(tx_hash)
            if get_transaction_data.status != GetTransactionStatus.NOT_FOUND:
                break
            time.sleep(self.wait_tx_interval)
        return get_transaction_data

    def invoke_contract_function(self, function_name, parameters=[]):
        """
        Invokes a function on the contract.

        Args:
            function_name (str): The name of the contract function.
            parameters (list, optional): The function parameters.

        Returns:
            Tuple[str, Any]: A tuple containing the transaction hash and the result of the function.
        """
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

        try:
            tx_hash, tx_data = self.send_tx(tx)
        except PrepareTransactionException as e:
            raise RuntimeError(
                f"Failed to prepare transaction: {e.simulate_transaction_response}"
            )
        if tx_data.status != GetTransactionStatus.SUCCESS:
            raise RuntimeError(f"Failed to send transaction: {tx_data}")

        return tx_hash, tx_data

    def is_tx_success(self, tx_data):
        return tx_data.status == GetTransactionStatus.SUCCESS

    def parse_tx_result(self, tx_data):
        assert tx_data.result_meta_xdr is not None
        transaction_meta = stellar_xdr.TransactionMeta.from_xdr(tx_data.result_meta_xdr)  # type: ignore
        # TODO handle multiple results[]
        assert transaction_meta.v3.soroban_meta
        result = transaction_meta.v3.soroban_meta.return_value
        return result

    def parse_sc_val(self, sc_val):
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
            return self.parse_sc_map(sc_val.map.sc_map)
        if sc_val.vec is not None:
            return self.parse_sc_vec(sc_val.vec)
        if sc_val.sym is not None:
            return sc_val.sym.sc_symbol.decode()
        raise ValueError("Could not parse sc_val")

    def parse_sc_vec(self, sc_vec):
        vec = []
        for val in sc_vec.sc_vec:
            vec.append(self.parse_sc_val(val))
        return vec

    def parse_asset_enum(self, sc_val):
        rust_asset_type = sc_val.vec.sc_vec[0].sym.sc_symbol.decode()
        if rust_asset_type == "Other":
            asset = sc_val.vec.sc_vec[1].sym.sc_symbol.decode()
            asset_type = "other"
        elif rust_asset_type == "Stellar":
            asset = Address.from_xdr_sc_address(sc_val.vec.sc_vec[1].address).address
            asset_type = "stellar"
        else:
            raise ValueError(f"Unexpected asset enum type: {rust_asset_type}")
        return (asset_type, asset)

    def parse_sc_asset_map(
        self, sc_asset_map
    ) -> Dict[Tuple[AssetType, str], List[Price]]:
        data = {}
        for entry in sc_asset_map:
            key = self.parse_asset_enum(entry.key)
            value = self.parse_sc_val(entry.val)
            data[key] = value
        return data

    def parse_sc_map(self, sc_map):
        data = {}
        for entry in sc_map:
            key = self.parse_sc_val(entry.key)
            value = self.parse_sc_val(entry.val)
            data[key] = value
        return data

    def parse_tx_data(self, tx_data, expect_asset_map=False):
        if self.is_tx_success(tx_data):
            result = self.parse_tx_result(tx_data)
            if result.type == SCValType.SCV_BOOL:
                return result.b
            elif result.type == SCValType.SCV_VOID:
                return
            elif result.type == SCValType.SCV_MAP:
                assert result.map is not None
                if expect_asset_map:
                    return self.parse_sc_asset_map(result.map.sc_map)
                return self.parse_sc_map(result.map.sc_map)
            elif result.type in [
                SCValType.SCV_U32,
                SCValType.SCV_I32,
                SCValType.SCV_U64,
                SCValType.SCV_I64,
                SCValType.SCV_U128,
                SCValType.SCV_I128,
                SCValType.SCV_SYMBOL,
            ]:
                return self.parse_sc_val(result)
            elif result.type == SCValType.SCV_ADDRESS:
                return str(result.address)
            elif result.type == SCValType.SCV_VEC:
                return self.parse_sc_vec(result.vec)
            else:
                raise ValueError(f"Unexpected result type: {result.type}")
        else:
            raise RuntimeError(f"Cannot parse unsuccessful transaction data: {tx_data}")

    def invoke_and_parse(self, function_name, parameters=[], expect_asset_map=False):
        """
        Invokes a contract function and parses the result.

        Args:
            function_name (str): The name of the contract function.
            parameters (list, optional): The function parameters.

        Returns:
            Tuple[str, Any]: A tuple containing the transaction hash and the parsed result of the function.
        """
        tx_hash, tx_data = self.invoke_contract_function(
            function_name,
            parameters,
        )
        return tx_hash, self.parse_tx_data(tx_data, expect_asset_map=expect_asset_map)

    def asset_to_asset_u32(self, asset_type: AssetType, asset: str) -> int:
        asset_u32 = ASSETS_TO_ASSET_U32.get((asset_type, asset))
        if asset_u32 is None:
            raise AssetU32NotFound(
                f"Asset has no u32 value: {asset_type} {asset}. Make sure to "
                "add a u32 value for this asset in ASSETS_TO_ASSET_U32."
            )
        return asset_u32

    def build_add_price_args(
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
        asset_u32 = self.asset_to_asset_u32(asset_type, asset)
        return [
            scval.to_uint32(source),
            self.build_asset_enum(asset_type, asset),
            scval.to_uint32(asset_u32),
            scval.to_int128(price_as_int),
            scval.to_uint64(timestamp),
        ]

    def initialize(
        self,
        admin: str,
        base_type: AssetType,
        base: str,
        decimals: int,
        resolution: int,
    ) -> Tuple[str, None]:
        """
        Initializes the contract with parameters.

        Args:
            admin (str): The admin's public key.
            base_type (AssetType): The base asset type ("stellar" or "other").
            base (str): The base asset identifier.
            decimals (int): The number of decimals for the contract.
            resolution (int): The resolution value for the contract.

        Returns:
            Tuple[str, None]: A tuple containing the transaction hash and None.
        """
        return self.invoke_and_parse(  # type: ignore
            "initialize",
            [
                scval.to_address(admin),
                self.build_asset_enum(base_type, base),
                scval.to_uint32(decimals),
                scval.to_uint32(resolution),
            ],
        )

    def write_admin(self) -> Tuple[str, None]:
        """
        Writes admin information to the contract.

        Raises:
            RuntimeError: Indicates that this feature is not yet available.
        """
        raise RuntimeError("This function is not yet available")

    def read_admin(self) -> Tuple[str, str]:
        """
        Reads the admin's public key from the contract.

        Returns:
            Tuple[str, str]: A tuple containing the transaction hash and the admin's public key.
        """
        return self.invoke_and_parse("read_admin")  # type: ignore

    def write_resolution(self, resolution: int) -> Tuple[str, None]:
        """
        Writes the resolution value to the contract.

        Returns:
            Tuple[str, None]: A tuple containing the transaction hash and None.
        """
        return self.invoke_and_parse("write_resolution", [scval.to_uint32(resolution)])  # type: ignore

    def sources(self) -> Tuple[str, List[int]]:
        """
        Retrieves the list of prices sources supported by the contract.

        Returns:
            Tuple[str, List[int]]: A tuple containing the transaction hash and a list of source IDs.
        """
        return self.invoke_and_parse("sources")  # type: ignore

    def prices_by_source(
        self, source: int, asset_type: AssetType, asset: str, records: int
    ) -> Tuple[str, List[Price]]:
        """
        Retrieves price records for a specific source, asset, and number of records.

        Args:
            source (int): The source ID.
            asset_type (AssetType): The asset type ("stellar" or "other").
            asset (str): The asset identifier. For off-chain assets, this is an empty string. For on-chain asset, this is the Soroban asset address (Token Interface).
            records (int): The number of records to retrieve.

        Returns:
            Tuple[str, List[Price]]: A tuple containing the transaction hash and a list of price records.
        """
        tx_hash, prices = self.invoke_and_parse(
            "prices_by_source",
            [
                scval.to_uint32(source),
                self.build_asset_enum(asset_type, asset),
                scval.to_uint32(records),
            ],
        )
        results = []
        for price in prices:  # type: ignore
            results.append(
                {
                    "price": str(Decimal(price["price"]) / DECIMAL_PLACES_DIVIDER),
                    "timestamp": price["timestamp"],
                }
            )
        return tx_hash, results

    def price_by_source(
        self, source: int, asset_type: AssetType, asset: str, timestamp: int
    ) -> Tuple[str, Optional[Price]]:
        """
        Retrieves a price record for a specific source, asset, and timestamp.

        Args:
            source (int): The source ID.
            asset_type (AssetType): The asset type ("stellar" or "other").
            asset (str): The asset identifier. For off-chain assets, this is an empty string. For on-chain asset, this is the Soroban asset address (Token Interface).
            timestamp (int): The timestamp of the price record.

        Returns:
            Tuple[str, Optional[Price]]: A tuple containing the transaction hash and the price record (or None if not found).
        """
        tx_hash, price = self.invoke_and_parse(  # type: ignore
            "price_by_source",
            [
                scval.to_uint32(source),
                self.build_asset_enum(asset_type, asset),
                scval.to_uint64(timestamp),
            ],
        )
        if price is not None:
            price = {
                "price": str(Decimal(price["price"]) / DECIMAL_PLACES_DIVIDER),  # type: ignore
                "timestamp": price["timestamp"],  # type: ignore
            }
        return tx_hash, price  # type: ignore

    def lastprice_by_source(
        self, source: int, asset_type: AssetType, asset: str
    ) -> Tuple[str, Optional[Price]]:
        """
        Retrieves the latest price record for a specific source and asset.

        Args:
            source (int): The source ID.
            asset_type (AssetType): The asset type ("stellar" or "other").
            asset (str): The asset identifier. For off-chain assets, this is an empty string. For on-chain asset, this is the Soroban asset address (Token Interface).

        Returns:
            Tuple[str, Optional[Price]]: A tuple containing the transaction hash and the latest price record (or None if not found).
        """
        tx_hash, price = self.invoke_and_parse(  # type: ignore
            "lastprice_by_source",
            [
                scval.to_uint32(source),
                self.build_asset_enum(asset_type, asset),
            ],
        )
        if price is not None:
            price = {
                "price": str(Decimal(price["price"]) / DECIMAL_PLACES_DIVIDER),  # type: ignore
                "timestamp": price["timestamp"],  # type: ignore
            }
        return tx_hash, price  # type: ignore

    def add_prices(self, prices: List[AssetPrice]) -> Tuple[str, None]:
        """
        Add prices to the contract.

        Args:
            prices (List[AssetPrice]): List of prices

        Returns:
            Tuple[str, None]: A tuple containing the transaction hash and None.
        """
        price_args = []
        for price in prices:
            try:
                add_price_args = self.build_add_price_args(
                    price["source"],
                    price["asset_type"],
                    price["asset"],
                    price["price"],
                    price["timestamp"],
                )
            except AssetU32NotFound as e:
                logging.warn(f"skipping price due to error: {e}")
                continue
            # see https://github.com/StellarCN/py-stellar-base/issues/815
            add_price_struct = scval.to_struct(
                {
                    "asset": add_price_args[1],
                    "asset_u32": add_price_args[2],
                    "price": add_price_args[3],
                    "source": add_price_args[0],
                    "timestamp": add_price_args[4],
                }
            )
            price_args.append(add_price_struct)
        price_args = scval.to_vec(price_args)
        args = [price_args]
        return self.invoke_and_parse("add_prices", args)  # type: ignore

    def update_contract(self, contract_wasm: Union[str, bytes]) -> Tuple[str, None]:
        """
        Updates the contract.

        Args:
            contract_wasm (Union[str, bytes]): The path to the contract, or binary data.

        Returns:
            Tuple[str, None]: A tuple containing the transaction hash and None.
        """
        deployer = OracleDeployer(
            signer=self.signer,
            network=self.network,  # type: ignore
            custom_network_passphrase=self.network_passphrase,
            custom_rpc_url=self.rpc_server_url,
            wait_tx_interval=self.wait_tx_interval,
            tx_timeout=self.tx_timeout,
        )
        wasm_id = deployer.upload_contract_wasm(contract_wasm)
        return self.invoke_and_parse("update_contract", [scval.to_bytes(bytes.fromhex(wasm_id))])  # type: ignore

    def lastprices_by_source_and_assets(
        self, source: int, assets: List[Asset]
    ) -> Tuple[str, dict]:
        """
        Retrieves the latest price records for a specific source and list of assets.
        Note: fetching too many assets might result in errors from Soroban due to return size limits.
        We recommend requesting no more than 15 assets at a time.

        Returns:
            Tuple[str, dict]: A tuple containing the transaction hash and a dict of latest price records.
        """
        asset_enums = []
        if len(assets) > 15:
            logging.warn(
                "fetching too many assets might result in errors from Soroban due to return size limits. We recommend requesting no more than 15 assets at a time.",
            )
        for asset in assets:
            asset_enums.append(
                self.build_asset_enum(asset["asset_type"], asset["asset"])
            )
        return self.invoke_and_parse(
            "lastprices_by_source_and_assets",
            [
                scval.to_uint32(source),
                scval.to_vec(asset_enums),
            ],
            expect_asset_map=True,
        )  # type: ignore

    def base(self) -> Tuple[str, Asset]:
        """
        Retrieves the base asset of the contract.

        Returns:
            Tuple[str, Asset]: A tuple containing the transaction hash and the base asset.
        """
        tx_hash, result = self.invoke_and_parse("base")
        if result[0] == "Other":  # type: ignore
            asset = Asset({"asset_type": "other", "asset": result[1]})  # type: ignore
        elif result[1] == "Stellar":  # type: ignore
            asset = Asset({"asset_type": "stellar", "asset": result[1]})  # type: ignore
        else:
            raise ValueError(f"Unexpected asset type: {result[1]}")  # type: ignore
        return tx_hash, asset

    def assets(self) -> Tuple[str, List[Asset]]:
        """
        Retrieves the list of supported assets by the contract.

        Returns:
            Tuple[str, List[Asset]]: A tuple containing the transaction hash and a list of supported assets.
        """
        tx_hash, results = self.invoke_and_parse("assets")
        assets = []
        for result in results:  # type: ignore
            if result[0] == "Other":  # type: ignore
                asset = Asset({"asset_type": "other", "asset": result[1]})  # type: ignore
            elif result[1] == "Stellar":  # type: ignore
                asset = Asset({"asset_type": "stellar", "asset": result[1]})  # type: ignore
            else:
                raise ValueError(f"Unexpected asset type: {result[1]}")  # type: ignore
            assets.append(asset)
        return tx_hash, assets

    def decimals(self):
        """
        Retrieves the number of decimals for the contract's assets.

        Returns:
            Tuple[str, Any]: A tuple containing the transaction hash and the number of decimals.
        """
        return self.invoke_and_parse("decimals")

    def resolution(self):
        """
        Retrieves the resolution value of the contract.

        Returns:
            Tuple[str, Any]: A tuple containing the transaction hash and the resolution value.
        """
        return self.invoke_and_parse("resolution")

    def price(
        self,
        asset_type: AssetType,
        asset: str,
        timestamp: int,
    ) -> Tuple[str, Optional[Price]]:
        """
        Retrieves a price record for a specific asset and timestamp.

        Args:
            asset_type (AssetType): The asset type ("stellar" or "other").
            asset (str): The asset identifier. For off-chain assets, this is an empty string. For on-chain asset, this is the Soroban asset address (Token Interface).
            timestamp (int): The timestamp of the price record.

        Returns:
            Tuple[str, Optional[Price]]: A tuple containing the transaction hash and the price record (or None if not found).
        """
        tx_hash, price = self.invoke_and_parse(
            "price",
            [
                self.build_asset_enum(asset_type, asset),
                scval.to_uint64(timestamp),
            ],
        )
        if price is not None:
            price = {
                "price": str(Decimal(price["price"]) / DECIMAL_PLACES_DIVIDER),  # type: ignore
                "timestamp": price["timestamp"],  # type: ignore
            }
        return tx_hash, price  # type: ignore

    def prices(
        self, asset_type: AssetType, asset: str, records: int
    ) -> Tuple[str, List[Price]]:
        """
        Retrieves price records for a specific asset and number of records.

        Args:
            asset_type (AssetType): The asset type ("stellar" or "other").
            asset (str): The asset identifier. For off-chain assets, this is an empty string. For on-chain asset, this is the Soroban asset address (Token Interface).
            records (int): The number of records to retrieve.

        Returns:
            Tuple[str, List[Price]]: A tuple containing the transaction hash and a list of price records.
        """
        tx_hash, prices = self.invoke_and_parse(
            "prices",
            [
                self.build_asset_enum(asset_type, asset),
                scval.to_uint32(records),
            ],
        )
        results = []
        for price in prices:  # type: ignore
            results.append(
                {
                    "price": str(Decimal(price["price"]) / DECIMAL_PLACES_DIVIDER),
                    "timestamp": price["timestamp"],
                }
            )
        return tx_hash, results

    def lastprice(
        self,
        asset_type: AssetType,
        asset: str,
    ) -> Tuple[str, Optional[Price]]:
        """
        Retrieves the latest price record for a specific asset.

        Args:
            asset_type (AssetType): The asset type ("stellar" or "other").
            asset (str): The asset identifier. For off-chain assets, this is an empty string. For on-chain asset, this is the Soroban asset address (Token Interface).

        Returns:
            Tuple[str, Optional[Price]]: A tuple containing the transaction hash and the latest price record (or None if not found).
        """
        tx_hash, price = self.invoke_and_parse(
            "lastprice",
            [
                self.build_asset_enum(asset_type, asset),
            ],
        )
        if price is not None:
            price = {
                "price": str(Decimal(price["price"]) / DECIMAL_PLACES_DIVIDER),  # type: ignore
                "timestamp": price["timestamp"],  # type: ignore
            }
        return tx_hash, price  # type: ignore

    def bump_instance(self, ledgers_to_live: int):
        """
        Bumps the contract instance.

        Returns:
            Tuple[str, None]: A tuple containing the transaction hash and None.
        """
        return self.invoke_and_parse("bump_instance", [scval.to_uint32(ledgers_to_live)])  # type: ignore


class OracleDeployer:
    def __init__(
        self,
        *,
        signer: Keypair,
        network: Network,
        custom_rpc_url: Optional[str] = None,
        custom_network_passphrase: Optional[str] = None,
        wait_tx_interval: int = 3,
        tx_timeout: int = 30,
    ):
        """
        Initializes an Oracle Deployer instance.

        Args:
            signer (Keypair): The keypair used to sign transactions.
            network (Network): The Stellar network to connect to (e.g., "futurenet", "testnet", "public").
            custom_rpc_url (str, optional): The custom RPC server URL. Default is None.
            custom_network_passphrase (str, optional): The custom network passphrase. Default is None.
            wait_tx_interval (int, optional): The interval to wait for a transaction (in seconds). Default is 3 seconds.
            tx_timeout (int, optional): The transaction timeout (in seconds). Default is 30 seconds.

        Returns:
            None
        """
        self.network = network
        if network == "standalone":
            self.network_passphrase = StellarSdkNetwork.STANDALONE_NETWORK_PASSPHRASE
            self.rpc_server_url = "http://localhost:8000/soroban/rpc"
        elif network == "futurenet":
            self.network_passphrase = StellarSdkNetwork.FUTURENET_NETWORK_PASSPHRASE
            self.rpc_server_url = "https://rpc-futurenet.stellar.org"
        elif network == "testnet":
            self.network_passphrase = StellarSdkNetwork.TESTNET_NETWORK_PASSPHRASE
            self.rpc_server_url = "https://soroban-testnet.stellar.org"
        elif network == "public":
            self.network_passphrase = StellarSdkNetwork.PUBLIC_NETWORK_PASSPHRASE
            self.rpc_server_url = "https://rpc.stellar.org:443/"
        elif network == "custom":
            if custom_rpc_url is None:
                raise ValueError("custom_rpc_url is required for custom network")
            if custom_network_passphrase is None:
                raise ValueError(
                    "custom_network_passphrase is required for custom network"
                )
            self.network_passphrase = custom_network_passphrase
            self.rpc_server_url = custom_rpc_url
        self.server = SorobanServer(self.rpc_server_url)
        self.signer = signer
        self.wait_tx_interval = wait_tx_interval
        self.tx_timeout = tx_timeout

    def upload_contract_wasm(self, contract_wasm: Union[str, bytes]):
        """
        Uploads a contract to the network.

        Args:
            contract_wasm (Union[str, bytes]): The path to the contract, or binary data.

        Returns:
            str: WASM id.
        """
        source_account = self.server.load_account(self.signer.public_key)
        tx = (
            TransactionBuilder(source_account, self.network_passphrase)
            .set_timeout(self.tx_timeout)
            .append_upload_contract_wasm_op(
                contract=contract_wasm,  # the path to the contract, or binary data
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
        return wasm_id

    def deploy(self, contract_wasm: Union[str, bytes]):
        """
        Deploys a contract.

        Args:
            contract_wasm (Union[str, bytes]): The path to the contract, or binary data.

        Returns:
            str: The contract ID.
        """
        wasm_id = self.upload_contract_wasm(contract_wasm)
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
