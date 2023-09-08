This is an example Contract that implements a very simple price up/down checks
against an Oracle contract.

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
export $REPO_DIR=$(pwd)
```

### Deploy the Lightecho Oracle

```
cd $REPO_DIR/oracle-onchain/sep40/contract

# build and run tests to make sure your toolchain is properly setup
make test

# load your Stellar secret key (can be any funded Stellar secret key)
source ./scripts/source_secret.sh

# deploy the Lightecho Oracle contract to the blockchain
./scripts/deploy.sh

```

Now, in order to invoke the deployed contract, we use our Python CLI.

### Setup the CLI

```
cd $REPO_DIR/oracle-onchain/sep40/cli
```

[Poetry](https://python-poetry.org/) is required to run the CLI:

```
curl -sSL https://install.python-poetry.org | python3 -
```

Make sure to add `$HOME/.local/bin` to your Shell startup file (e.g. `~/.bashrc`),
otherwise the `poetry` program might not be found.

Install the CLI Poetry dependencies:

```
./poetry_install.sh
```

Create CLI `local_settings.py`:

```
SOURCE_SECRET = "SBKEDTLZ6DACGUDTBL7O2LPTEW46KGVZUEXSQGEXCBE5KFKZGDCD4YWW"
ADMIN_SECRET = "SDFWYGBNP5TW4MS7RY5D4FILT65R2IEPWGL34NY2TLSU4DC4BJNXUAMU"
ORACLE_CONTRACT_ID = "<oracle contract id deployed above>"
PRICEUPDOWN_CONTRACT_ID = "" # we'll fill this later below

RPC_SERVER_URL = "https://rpc-futurenet.stellar.org:443/"
NETWORK_PASSPHRASE = "Test SDF Future Network ; October 2022"
```

### Initialize the Lightecho Oracle

```
./cli oracle initialize \
  GDOOLD2UL3STZ4FLHM5CV3ZFSTYI4EYZHEEGIC4GHL4CJ4BLSSYNN5ER \
  XLM \
  18 \
  300

# add a price to the oracle
# NOTE: this is throwing an error due to issues with Stellar authorization, see:
#    https://github.com/StellarCN/py-stellar-base/issues/773
./cli oracle add_price 0 other USD 5.5
```

### Deploy the PriceUpDown contract

```
cd $REPO_DIR/oracle-onchain/sep40/examples/price_up_down

# build and run tests to make sure your toolchain is properly setup
make test

# load your Stellar secret key (can be any funded Stellar secret key)
source ./scripts/source_secret.sh

# deploy the PriceUpDown contract to the blockchain
./scripts/deploy.sh
```

### Add the contract id to the CLI `local_settings.py`:
```
cd $REPO_DIR/oracle-onchain/sep40/cli
edit local_settings.py
```
`local_settings.py`:
```
...
PRICEUPDOWN_CONTRACT_ID = "<priceupdown contract id deployed above>"
...
```

### Initialize the PriceUpDown contract

```
./cli priceupdown initialize \
  <oracle contract id from above>

./cli priceupdown get_price_up_down \
  other \
  USD
```
