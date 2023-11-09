# SEP-40 Consumer Contract Example

This is an example implementation of a Soroban contract written in Rust that
implements a very simple price up/down check against an Oracle contract.  
To invoke the contract, you can use the [Python-based CLI](./cli).

This contract contains three functions:

- `initialize`: initialize the contract with an Oracle contract id
- `lastprice`: returns latest asset price directly from the Oracle
- `get_price_up_down`: returns an enum:

  ```
  UpDown {
      up: false,
      down: false,
      equal: false,
  }
  ```

  - `up` will be `true` if current price is above the previous checked price.
  - `down` will be `true` if current price is below the previous checked price.
  - `equal` will be `true` if current price is the same the previous checked price.

  When this function is called, it will fetch the latest price from an Oracle
  and store it internally. The next time this function called, the latest price
  is fetched again and compared to the previously fetched price, and so on.

## Deploying this contract

This contract requires an existing [SEP40](https://github.com/stellar/stellar-protocol/blob/master/ecosystem/sep-0040.md)-compatible Oracle contract for providing the prices.  
For this example we'll be using our own [Lightecho Oracle](https://github.com/bp-ventures/lightecho-stellar-oracle/tree/trunk/oracle-onchain/sep40/contract) contract as the Oracle.

### Setup Rust and Soroban CLI

Install the Soroban toolchain by following the official guide:  
https://soroban.stellar.org/docs/getting-started/setup

Clone this repository:

```
git clone https://github.com/bp-ventures/lightecho-stellar-oracle.git
cd lightecho-stellar-oracle
export REPO_DIR=$(pwd)
```


### Deploy the contract

```
# build and run tests to make sure your toolchain is properly setup
make test

# load your Stellar secret key (can be any funded Stellar secret key)
source ./scripts/source_secret.sh

# deploy the PriceUpDown contract to the blockchain
./scripts/deploy.sh
```

![Screenshot_20230913_105510](https://github.com/bp-ventures/lightecho-stellar-oracle/assets/26092447/a4156733-cd57-4265-805a-20af12ab38ec)


### Initialize the contract via CLI

See [CLI instructions](./cli/README.md)
