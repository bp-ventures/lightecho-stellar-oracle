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

[Poetry](https://python-poetry.org/) is required to run the deployment scripts.

```
# load stellar source account secret key into environment
source ./scripts/source_secret.sh

# deploy and initialize contract
./scripts/deploy.sh <admin> <base> <decimals> <resolution>
```
