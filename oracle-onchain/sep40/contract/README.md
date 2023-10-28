**Lightecho Oracle contract Rust source code**

For more information see docs at https://github.com/bp-ventures/lightecho-stellar-oracle

**TESTNET** Official Contracts:
- Base `XLM`:
  ```
  CDYHDC7OPAWPQ46TGT5PU77C2NWFGERD6IQRKVNBL34HCXHARWO24XWM
  ```
- Base `USD`:
  ```
  CAC6JWJG22ULRNGY75H2NVDIXQQP5JRJPERTZXXXONJHD2ETMGGEV7WP
  ```

# Consuming the Oracle from another Soroban contract

See the [PriceUpDown contract example](../examples/price_up_down) on how to consume the Oracle from another
Soroban contract.

# Deploying a new Oracle instance

These instructions are for deploying a new Oracle instance to the blockchain.  
Note that if you deploy a new Oracle instance, the instance will not contain
any price unless you feed the prices yourself. So we highly recommend not
deploying a new instance, and instead, [fetch prices from our official Oracle contract](#fetching-prices-from-the-oracle).

## Install Soroban Rust toolchain

Follow the instructions in https://soroban.stellar.org/docs/getting-started/setup.

## Install GNU build tools

- For Ubuntu:

```
sudo apt install build-essential
```

- For other operating systems, please check the documentation of your specific system.
  Make sure GNU `make` is available along with its related tools.

## Deploy contract to the blockchain

```
# load stellar source account secret key into environment
source ./scripts/source_secret.sh

# deploy the contract to the blockchain
./scripts/deploy.sh
```

## Initialize contract via CLI

We provide a Python-based CLI for interacting with the deployed contract.

Install [Poetry](https://python-poetry.org/):

```
curl -sSL https://install.python-poetry.org | python3 -
```

Make sure to add `$HOME/.local/bin` to your Shell startup file (e.g. `~/.bashrc`),
otherwise the `poetry` program might not be found.

Go to CLI dir:

```
cd ../cli
```

Install CLI dependencies:

```
./poetry_install.sh
```

Create CLI `local_settings.py` file, and edit it with your deployed Oracle contract id:

```
SOURCE_SECRET = "<stellar source secret you used above>"
ADMIN_SECRET = "<stellar secret key of contract admin>"

ORACLE_CONTRACT_ID = "<oracle contract id you obtained above>"
PRICEUPDOWN_CONTRACT_ID = "" # leave empty

RPC_SERVER_URL = "https://rpc-futurenet.stellar.org:443/"
NETWORK_PASSPHRASE = "Test SDF Future Network ; October 2022"
```

Initialize the contract:

```
./cli oracle initialize <admin> <base> <decimals> <resolution>
```

Example:

```
./cli oracle initialize \
    GCDXRFUE3OCQLIUYYCQHOS2TPEZ5VMVSVRXEOBQDUJRRGP67IXRFPS7T
    XLM
    18
    300
```
