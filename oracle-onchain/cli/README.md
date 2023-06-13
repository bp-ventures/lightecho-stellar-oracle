Create `local_settings.py`:

```

from stellar_sdk import Network

SOURCE_SECRET = "SBKEDTLZ6DACGUDTBL7O2LPTEW46KGVZUEXSQGEXCBE5KFKZGDCD4YWW"
RPC_SERVER_URL = "https://rpc-futurenet.stellar.org:443/"
CONTRACT_ID = "1ecc0d06e4713e314d0e5f7ebbb8398e2cc8cf7f4168c99dbb511ed1ca327409"
NETWORK_PASSPHRASE = "Test SDF Future Network ; October 2022"

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
