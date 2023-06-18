Create `local_settings.py`:

```

from stellar_sdk import Network

SOURCE_SECRET = "SBKEDTLZ6DACGUDTBL7O2LPTEW46KGVZUEXSQGEXCBE5KFKZGDCD4YWW"

# admin source secret (required for changing base or setting rates):
#SOURCE_SECRET = "SDFWYGBNP5TW4MS7RY5D4FILT65R2IEPWGL34NY2TLSU4DC4BJNXUAMU"

RPC_SERVER_URL = "https://rpc-futurenet.stellar.org:443/"
CONTRACT_ID = "225bd2966e21977e99d0360d00663c41db77fe0d2b234b438b8b3eb425f9f22f"
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
