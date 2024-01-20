**Lightecho Oracle - Oracle smart contract for Soroban**

**We're in the middle of a major transition in the contract structure, many
things are not working right now. If you encounter any issues please create
a ticket in GitHub.**

TODO light version:
- DONE deploy to testnet
- DONE feed some prices
- python sdk
  - DONE review code
  - DONE run unit tests
- cli
  - DONE test all functions
  - DONE test feed scripts
- javascript sdk
  - DONE review code
- DONE deploy official testnet XLM
- DONE update contract id python sdk
- DONE publish python sdk
- DONE update contract id javascript sdk
- DONE publish javascript sdk
- DONE server stop systemd units
- DONE pull in server
- DONE poetry install in server
- DONE initialize contract
- DONE fix feed script to always feed with current normalized timestamp
- test feed bulk
- restart systemd units
- check website to see if prices are there
- diagrams
- faq
- update README.md explaining how good the contract is right now
- metrics (how to collect?)

Lightecho is a Stellar Oracle for emerging markets data and XLM volatility feeds.

This repository contains:

- Interacting with the Contract (e.g. fetch prices, add prices)
  - [Python-based CLI](./oracle-onchain/sep40/cli)
  - Web app
    - [Visit web app](https://bp-ventures.github.io/lightecho-stellar-oracle/)
    - [Web app source code](./docs/v2.html)
  - [A JS fiddle for testing and debugging the contract calls](https://playcode.io/1678393)
  - [Example on how to use the Oracle from a consumer contract (in Rust)](./oracle-onchain/sep40/examples/price_up_down)
- Developer tools
  - [Python SDK](./oracle-sdk/python)
  - [JavaScript SDK](./oracle-sdk/javascript)
  - Oracle contract implementation for the Soroban Smart Contracts platform
    - [Contract source code](./oracle-onchain/sep40/contract)
    - [SEP-40 specification](https://github.com/stellar/stellar-protocol/blob/master/ecosystem/sep-0040.md)
  - [Infrastructure Diagram](./INFRASTRUCTURE.md)

**TESTNET** Official Contracts:

- Base `XLM`:
  ```
  CDRKPQZGDW7F3BGQNXXQIIMTGLIKRD3RGN46HZBGBAX46TR6B4YEZQQU
  ```
- Base `USD`:
  ```
  CD25CPJMPZIJ44JM3TCUW43M5OGMLTHKVLIVRCOS55C6LBYFL5Y2GGRU
  ```

**TESTNET** Official Sources for prices:

```
0 - BPV aggregator
1 - Coinbase
```

Each source is represented by an integer in the blockchain contract.
To fetch the last price of USD from Coinbase for example, you can use the CLI:

```
./cli oracle lastprice_by_source 1 other USD
```

### Roadmap

- Complete JS examples
- Improve documentation
- Deploy market data feeds for XLM/EUR, XLM/USD, XLM/ARS, XLM/BRL, XLM/NGN, XLM/NGN_2 and a test of XLM Vol
- Confirm prices resolution
- Improved documentation
- Uptime monitoring for feeds
- Diversity of feeds (2+ organizations)
- Bounty for usage
- Soroban go live (pilot mode)
- Soroban Production```

#### Install the price feed script

The price feed is a script that puts the prices into the blockchain contract.

```bash
sudo apt install systemd-container
sudo machinectl shell myusername@  # replace myusername with your Linux username
mkdir -p ~/.config/systemd/user/
cp init/systemd/* ~/.config/systemd/user/
systemctl --user enable feed_bulk_from_db.timer bump_instance.timer
systemctl --user start feed_bulk_from_db.timer bump_instance.timer

# to check status
./systemd-status.sh

# to see logs
journalctl --user -u feed_bulk_from_db
journalctl --user -u bump_instance
```

#### Featured projects

Have a project that uses our Oracle? Feel free to share with us and we'll be happy to list it here!

---

https://lightecho.io

_Made by BP Ventures_
