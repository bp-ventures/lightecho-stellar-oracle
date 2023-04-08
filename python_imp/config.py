from stellar_sdk import Network
from stellar_sdk.soroban import SorobanServer

rpc_server_url = "https://horizon-futurenet.stellar.cash:443/soroban/rpc"
soroban_server = SorobanServer(rpc_server_url)
network_passphrase = Network.TESTNET_NETWORK_PASSPHRASE
