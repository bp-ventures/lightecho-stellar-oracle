from stellar_sdk import Network
from stellar_sdk.soroban import SorobanServer

rpc_server_url = "https://rpc-futurenet.stellar.org:443/"
soroban_server = SorobanServer(rpc_server_url)
network_passphrase = Network.FUTURENET_NETWORK_PASSPHRASE
secret = "SCNLUY7SFXJYVIULV66V2OQHNB4XDWYFGNNCN5YBBC3MZT5XN4X7IJP6"
