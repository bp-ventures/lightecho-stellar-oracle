# Oracle for prices management

## Description

This app lets you create, update, get and delete prices associated with seller Address using the oracle setter and getter.

## Usage

### Create a price

To create a price, you need to send a transaction to the oracle setter with the following parameters:

- `contract_id` - contract id of the oracle
- `sellar` - seller address of the user
- `sell_price` - price of the asset
- `buy_price` - price of the asset

### Update a price

To update a price, you need to send a transaction to the oracle setter with the following parameters:

- `contract_id` - contract id of the oracle
- `sellar` - seller address of the user
- `sell_price` - price of the asset
- `buy_price` - price of the asset

### Get a price

To get a price, you need to send a transaction to the oracle getter with the following parameters:

- `contract_id` - contract id of the oracle

### Delete a price

To delete a price, you need to send a transaction to the oracle setter with the following parameters:

- `contract_id` - contract id of the oracle

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
target/wasm32-unknown-unknown/release/manage_prices.wasm
```

### Deploy

```
soroban contract deploy --wasm target/wasm32-unknown-unknown/release/manage_prices.wasm
```

### Invoke the contract

Invoke create function

```
soroban contract invoke \
    --wasm target/wasm32-unknown-unknown/release/manage_prices.wasm
    --id [contract_id] \
    -- create \
    --seller "GAD77QJZFQSYMYL2ORVBJBKFJCYKOXFLGIROY3TAL6Z6R4HMFKBY2C2B"
    --sell_price 1
    --buy_price 1
```

Invoke update function

```
soroban contract invoke \
    --wasm target/wasm32-unknown-unknown/release/manage_prices.wasm
    --id [contract_id] \
    -- update \
    --seller "GAD77QJZFQSYMYL2ORVBJBKFJCYKOXFLGIROY3TAL6Z6R4HMFKBY2C2B"
    --sell_price 1
    --buy_price 1
```

Invoke get price function

````
soroban contract invoke \
    --wasm target/wasm32-unknown-unknown/release/manage_prices.wasm
    --id [contract_id] \
    -- get
```

Invoke delete function

````

soroban contract invoke \
 --wasm target/wasm32-unknown-unknown/release/manage_prices.wasm
--id [contract_id] \
 -- delete

### Python Integration

To invoke deployed contract from python, you can see [soroban-py](./soroban-py/README.md) documentation.

## License

This project is licensed under the MIT License - see the [License](./LICENSE.md) file for details
