This is a Python-based CLI that can be used as an utility to invoke the
Oracle contract.

Create `local_settings.py`:

```
SOURCE_SECRET = "SBKEDTLZ6DACGUDTBL7O2LPTEW46KGVZUEXSQGEXCBE5KFKZGDCD4YWW"
ADMIN_SECRET = "SDFWYGBNP5TW4MS7RY5D4FILT65R2IEPWGL34NY2TLSU4DC4BJNXUAMU"

ORACLE_CONTRACT_ID = "" # empty by default, but you must put the oracle contract id here later

RPC_URL="https://my-custom-rpc.mydomain.com"
NETWORK_PASSPHRASE="Test SDF Network ; September 2015"
HORIZON_URL="https://horizon-testnet.stellar.org"
ADD_PRICES_SUCCESS_HEARTBEAT_URL="https://sm.hetrixtools.net/hb/?s=..."
```

```
poetry install

./cli --help
```
