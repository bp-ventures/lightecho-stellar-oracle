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

[Poetry](https://python-poetry.org/) is required to run the deployment scripts:
```
curl -sSL https://install.python-poetry.org | python3 -
```

Make sure to add `$HOME/.local/bin` to your Shell startup file (e.g. `~/.bashrc`),
otherwise the `poetry` program might not be found.

```
# load stellar source account secret key into environment
source ./scripts/source_secret.sh

# install CLI dependencies
$REPO_DIR/oracle-onchain/sep40/cli/poetry_install.sh

# deploy the contract to the blockchain
./scripts/deploy.sh

# initialize the contract
cd ../cli
./cli initialize <admin> <base> <decimals> <resolution>
```
