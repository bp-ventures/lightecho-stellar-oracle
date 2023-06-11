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
    --source SCXNO6G4LFNSGSI4KGE3BL6XMRXZM7G34MNLAFUEIHMN7PUIWVEOITT7 \
    --rpc-url https://rpc-futurenet.stellar.org:443 \
    --network-passphrase 'Test SDF Future Network ; October 2022'

soroban contract invoke \
    --id 63830c13aafd7bf01dee8e5b2f256d98b59621ddc2007e673dbea1f928508ad9 \
    --source SCXNO6G4LFNSGSI4KGE3BL6XMRXZM7G34MNLAFUEIHMN7PUIWVEOITT7 \
    --rpc-url https://rpc-futurenet.stellar.org:443 \
    --network-passphrase 'Test SDF Future Network ; October 2022' \
    -- \
    get-price \
    --to friend
```
