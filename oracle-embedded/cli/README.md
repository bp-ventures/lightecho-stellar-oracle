Create `local_settings.py`:

```

from stellar_sdk import Network

SOURCE_SECRET = "SCXNO6G4LFNSGSI4KGE3BL6XMRXZM7G34MNLAFUEIHMN7PUIWVEOITT7"
RPC_SERVER_URL = "https://rpc-futurenet.stellar.org:443/"
CONTRACT_ID = "4426723b6edc323e15addb3c1700f142d806fd546a36ce7a3cd05f776eb42b82"
NETWORK_PASSPHRASE = Network.FUTURENET_NETWORK_PASSPHRASE

```

```
poetry install

./cli.py --help
./cli.py set-base USD
./cli.py get-base
./cli.py get-base
./cli.py set-rate USDC 1234 0 4.24
./cli.py get-rate USDC 1234 0
```
