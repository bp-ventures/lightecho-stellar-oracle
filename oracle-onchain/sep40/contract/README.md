Lightecho Oracle contract Rust source code.

For more information see docs at https://github.com/bp-ventures/lightecho-stellar-oracle

- [Development setup](#development-setup)
- [Production deployment](#production-deployment)

# Development setup

# Setup Rust and Soroban

Follow instructions from Stellar docs:  
https://soroban.stellar.org/docs/getting-started/setup

```
make

soroban contract deploy \
    --wasm target/wasm32-unknown-unknown/release/oracle.wasm \
    --source SBKEDTLZ6DACGUDTBL7O2LPTEW46KGVZUEXSQGEXCBE5KFKZGDCD4YWW \
    --rpc-url https://rpc-futurenet.stellar.org:443 \
    --network-passphrase 'Test SDF Future Network ; October 2022'

# Run on Sandbox
soroban contract invoke \
    --wasm target/wasm32-unknown-unknown/release/oracle.wasm \
    --id 1 \
    -- \
    initialize \
    --admin GDOOLD2UL3STZ4FLHM5CV3ZFSTYI4EYZHEEGIC4GHL4CJ4BLSSYNN5ER \
    --base '{"Other":"XLM"}' \
    --decimals 18 \
    --resolution 1
```

# Production deployment

## Deploy contract

```
# load stellar source account secret key into environment
source ./scripts/source_secret.sh

# deploy the contract to the blockchain
./scripts/deploy.sh
```

## Initialize contract

[Poetry](https://python-poetry.org/) is required to run the CLI:
```
curl -sSL https://install.python-poetry.org | python3 -
```

Make sure to add `$HOME/.local/bin` to your Shell startup file (e.g. `~/.bashrc`),
otherwise the `poetry` program might not be found.

Go to CLI dir:
```
cd ../cli
```

Install CLI dependencies:
```
./poetry_install.sh
```

Create CLI `local_settings.py` file, and edit it with your deployed Oracle contract id:
```
SOURCE_SECRET = "<stellar source secret you used above>"
ADMIN_SECRET = "<stellar secret key of contract admin>"
ORACLE_CONTRACT_ID = "<oracle contract id you obtained above>"
PRICEUPDOWN_CONTRACT_ID = "" # leave empty as it's not required for the Oracle contract

RPC_SERVER_URL = "https://rpc-futurenet.stellar.org:443/"
NETWORK_PASSPHRASE = "Test SDF Future Network ; October 2022"
```

Initialize the contract:
```
./cli oracle initialize <admin> <base> <decimals> <resolution>
```
