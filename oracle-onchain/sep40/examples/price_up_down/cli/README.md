### Install Poetry

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

### Create local settings

Create `local_settings.py`:

```
SOURCE_SECRET = "SBKEDTLZ6DACGUDTBL7O2LPTEW46KGVZUEXSQGEXCBE5KFKZGDCD4YWW"
ADMIN_SECRET = "SDFWYGBNP5TW4MS7RY5D4FILT65R2IEPWGL34NY2TLSU4DC4BJNXUAMU"
ORACLE_CONTRACT_ID = ""  # contract id of the deployed Oracle contract
PRICEUPDOWN_CONTRACT_ID = ""  # contract id of the deployed PriceUpDown contract
STELLAR_NETWORK="testnet"  # testnet, futurenet or public
```

### Initialize the contract

```
./cli priceupdown initialize
```

### Get price up/down value

```
./cli priceupdown get_price_up_down other USD
```

### Other commands

```
./cli priceupdown --help
```
