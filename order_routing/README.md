# Soroban: Order Routing Smart Contract

# Setup
To build and develop contracts you need only a couple prerequisites:

- A [Rust](https://www.rust-lang.org/) toolchain
- An editor that supports Rust
- [Soroban CLI](https://soroban.stellar.org/docs/getting-started/setup#install-the-soroban-cli)

# Install RUST
```
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```
# Install the target
```
rustup target add wasm32-unknown-unknown
```
# Install the Soroban CLI
```
cargo install --locked --version 0.6.0 soroban-cli
```
# Usagae
Run the **soroban** command and you shoudl see the output like below

```
soroban
```

<img src="https://user-images.githubusercontent.com/46220827/226283228-ce567784-f1c4-489f-bdb0-0c477ecdc0d8.png" width="500">

# Run the Tests

```
cargo test
```

# Build

```
cargo build --target wasm32-unknown-unknown --release
```

A `.wasm` file will be outputted in the `target` directory. The `.wasm` file is the built contract.

```
target/wasm32-unknown-unknown/release/soroban_order.wasm
```

# Run on Sandbox
```
soroban contract invoke \
    --wasm ../target/wasm32-unknown-unknown/release/soroban_order.wasm \
    --id [id] \
    --fn [functon_name]
```

# Deploy to Futurenet
To run a local node for the [Futurenet] network with the Stellar Quickstart Docker image, run the following command.

```
docker run --rm -it \
  -p 8000:8000 \
  --name stellar \
  stellar/quickstart:soroban-dev \
  --futurenet \
  --enable-soroban-rpc
```

Once the image is started you can check its status by querying the Horizon API:

```
curl http://localhost:8000
```

It takes sometime to join a remote network. Monitor the output of that endpoint until you see the `core_latest_ledger` become a number above zero.

Generate a key by going to the [Stellar Laboratory]. Make note of both the `G...` and `S...` keys. The `G...` key is the public key and will also be the account ID. The `S...` key is the secret key and is that you use to control the account.

Create an account on the [Futurenet] network by making a request to the Friendbot. Specify as the `addr` the `G...` key of your account.

```
curl "https://friendbot-futurenet.stellar.org/?addr=G..."
```

Once you have an account on the network, we'll use the code we wrote in [Write a Contract] and the resulting `.wasm` file we built in [Build] as our contract to deploy. Run the following commands to deploy the contract to the network. Use the `S...` key as the secret key.

```
soroban contract deploy \
    --wasm target/wasm32-unknown-unknown/release/soroban_order.wasm \
    --secret-key [secret] \
    --rpc-url http://localhost:8000/soroban/rpc \
    --network-passphrase 'Test SDF Future Network ; October 2022'
```

Using the contract ID that was outputted, use the [`soroban-cli`] to invoke the function of the contract.

```
soroban contract invoke \
    --id [id] \
    --secret-key [secret] \
    --rpc-url http://localhost:8000/soroban/rpc \
    --network-passphrase 'Test SDF Future Network ; October 2022' \
    --fn [function_name] 
```
