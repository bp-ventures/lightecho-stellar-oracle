Create `local_settings.py`:

```

from stellar_sdk import Network

SOURCE_SECRET = "SBKEDTLZ6DACGUDTBL7O2LPTEW46KGVZUEXSQGEXCBE5KFKZGDCD4YWW"

# admin source secret (required for changing base or setting rates):
#SOURCE_SECRET = "SDFWYGBNP5TW4MS7RY5D4FILT65R2IEPWGL34NY2TLSU4DC4BJNXUAMU"

RPC_SERVER_URL = "https://rpc-futurenet.stellar.org:443/"
CONTRACT_ID = "65e9f660742a626bfac85222953bb689345974520afea512f2a500fbc2b5f039"
NETWORK_PASSPHRASE = "Test SDF Future Network ; October 2022"

```

```
poetry install

./cli --help
```
