Lightecho Oracle contract Rust source code.

For more information see docs at https://github.com/bp-ventures/lightecho-stellar-oracle

# Development setup

# Setup Rust and Soroban

Follow instructions from Stellar docs:  
https://soroban.stellar.org/docs/getting-started/setup

```
cargo build --target wasm32-unknown-unknown --release

soroban contract deploy \
    --wasm target/wasm32-unknown-unknown/release/oracle.wasm \
    --source SBKEDTLZ6DACGUDTBL7O2LPTEW46KGVZUEXSQGEXCBE5KFKZGDCD4YWW \
    --rpc-url https://rpc-futurenet.stellar.org:443 \
    --network-passphrase 'Test SDF Future Network ; October 2022'

soroban contract invoke \
    --id <contract id obtained in above step> \
    --source SBKEDTLZ6DACGUDTBL7O2LPTEW46KGVZUEXSQGEXCBE5KFKZGDCD4YWW \
    --rpc-url https://rpc-futurenet.stellar.org:443 \
    --network-passphrase 'Test SDF Future Network ; October 2022' \
    -- \
    get-price \
    --to friend
```
