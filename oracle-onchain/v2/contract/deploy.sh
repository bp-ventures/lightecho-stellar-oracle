#!/usr/bin/env bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR"

echo -n "Enter source secret (your input will be hidden): "
read -s source_secret

cargo build --target wasm32-unknown-unknown --release

soroban contract deploy \
    --wasm target/wasm32-unknown-unknown/release/oracle.wasm \
    --source "$source_secret" \
    --rpc-url https://rpc-futurenet.stellar.org:443 \
    --network-passphrase 'Test SDF Future Network ; October 2022'
