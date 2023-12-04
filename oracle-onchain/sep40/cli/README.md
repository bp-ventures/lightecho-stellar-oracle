This is a Python-based CLI that can be used as an utility to invoke the
Oracle contract.

Create `local_settings.py`:

```
SOURCE_SECRET = "SBKEDTLZ6DACGUDTBL7O2LPTEW46KGVZUEXSQGEXCBE5KFKZGDCD4YWW"
ADMIN_SECRET = "SDFWYGBNP5TW4MS7RY5D4FILT65R2IEPWGL34NY2TLSU4DC4BJNXUAMU"

ORACLE_CONTRACT_ID = "" # empty by default, but you must put the oracle contract id here later

STELLAR_NETWORK="testnet"  # standalone, testnet, futurenet or public
```

```
poetry install

./cli --help
```
