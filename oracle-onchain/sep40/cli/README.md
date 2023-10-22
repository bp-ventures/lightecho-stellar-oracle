This is a Python-based CLI that can be used as an utility to deploy and invoke
contracts in this repository:
- `oracle` contract
- `priceupdown` contract

Create `local_settings.py`:

```
SOURCE_SECRET = "SBKEDTLZ6DACGUDTBL7O2LPTEW46KGVZUEXSQGEXCBE5KFKZGDCD4YWW"
ADMIN_SECRET = "SDFWYGBNP5TW4MS7RY5D4FILT65R2IEPWGL34NY2TLSU4DC4BJNXUAMU"

ORACLE_CONTRACT_ID = "" # empty by default, but you must put the oracle contract id here later
PRICEUPDOWN_CONTRACT_ID = "" # empty by default, but you must put the priceupdown contract id here later

RPC_SERVER_URL = "https://soroban-testnet.stellar.org"
NETWORK_PASSPHRASE = "Test SDF Network ; September 2015"
HORIZON_URL = "https://horizon-testnet.stellar.org"
```

```
poetry install

./cli --help
```
