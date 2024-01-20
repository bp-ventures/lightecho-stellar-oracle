**Lightecho Oracle - Oracle smart contract for Soroban**

Lightecho is a Stellar Oracle for emerging markets data and XLM volatility feeds.

This repository contains:

- Interacting with the Contract (e.g. fetch prices, add prices)
  - Web app
    - [Visit web app](https://bp-ventures.github.io/lightecho-stellar-oracle/)
    - [Web app source code](./docs/v2.html)
  - [Python-based CLI](./oracle-onchain/sep40/cli)
  - [(outdated) A JS fiddle for testing and debugging the contract calls](https://playcode.io/1678393)
  - [(outdated) Example on how to use the Oracle from a consumer contract (in Rust)](./oracle-onchain/sep40/examples/price_up_down)
- Developer tools
  - [Python SDK](./oracle-sdk/python)
  - [JavaScript SDK](./oracle-sdk/javascript)
  - Oracle contract implementation for the Soroban Smart Contracts platform
    - [Contract source code](./oracle-onchain/sep40/contract)
    - [SEP-40 specification](https://github.com/stellar/stellar-protocol/blob/master/ecosystem/sep-0040.md)
  - [Infrastructure Diagram](./INFRASTRUCTURE.md)

**TESTNET** Official Contracts:

- Base `XLM`: [CA2IT45Y5X4EPXMDF5W4BGXVHQ2HZCY6TTQVJYQJQ5IBD2F4Z6UPPC7P](https://stellar.expert/explorer/testnet/contract/CA2IT45Y5X4EPXMDF5W4BGXVHQ2HZCY6TTQVJYQJQ5IBD2F4Z6UPPC7P)
- Base `USD`: `not deployed yet`

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

- diagrams
- faq
- update README.md explaining design decisions
- metrics (how to collect?)
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
