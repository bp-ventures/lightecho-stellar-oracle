# Get XLM balance of a contract

This example shows how to get the XLM balance of a contract.

## How to run

### Prerequisites

- A [Rust](https://www.rust-lang.org/) toolchain
- An editor that supports Rust
- [Soroban CLI](https://soroban.stellar.org/docs/getting-started/setup#install-the-soroban-cli)

### Run the Tests

```
cargo test
```

### Build

```
cargo build --target wasm32-unknown-unknown --release
```

A `.wasm` file will be outputted in the `target` directory. The `.wasm` file is the built contract.

```
target/wasm32-unknown-unknown/release/xlm_balance_contract.wasm
```

## Deploy

### Deploy on Testnet

```
soroban contract deploy --wasm target/wasm32-unknown-unknown/release/xlm_balance_contract.wasm
```

### Deploy on FUTURENET

```
soroban contract deploy \
    --wasm target/wasm32-unknown-unknown/release/xlm_balance_contract.wasm \
    --source [secret_key] \
    --rpc-url https://rpc-futurenet.stellar.org:443 \
    --network-passphrase 'Test SDF Future Network ; October 2022'
```

### Invoke the contract

Invoke create function

```
soroban contract invoke \
    --wasm target/wasm32-unknown-unknown/release/xlm_balance_contract.wasm
    --id [contract_id] \
    --rpc-url "https://rpc-futurenet.stellar.org:443" \
    --network-passphrase "Test SDF Future Network ; October 2022" \
    -- balance \
    --address "GAD77QJZFQSYMYL2ORVBJBKFJCYKOXFLGIROY3TAL6Z6R4HMFKBY2C2B"
    --token_id d93f5c7bb0ebc4a9c8f727c5cebc4e41194d38257e1d0d910356b43bfc528813
```
