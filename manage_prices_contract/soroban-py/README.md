# Soroban Python Implementation

## Description

This app lets you invoke functions of deployed contract on the FUTURENET network.

## Prerequisites

- Python 3.7 or higher
- Stellar SDK
  ```
  pip install git+https://github.com/StellarCN/py-stellar-base@soroban#egg=stellar-sdk
  ```

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

```
python main.py
```

## How to test

Press `1` to create a price
