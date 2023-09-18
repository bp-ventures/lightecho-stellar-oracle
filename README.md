**Lightecho Oracle - Oracle smart contract for Soroban**

Lightecho is a Stellar Oracle for emerging markets data and XLM volatility feeds.

**Update 2023-Sep-18:**
Due to the latest Futurenet reset and Soroban SDK updates, most of our codebase is not
working and we're currently fixing the issues.

This repository contains:

- Oracle contract implementation for the Soroban Smart Contracts platform
  - [Contract source code](./oracle-onchain/sep40/contract)
  - [SEP-40 specification](https://github.com/stellar/stellar-protocol/blob/master/ecosystem/sep-0040.md)
- A Python-based CLI for interacting with the deployed contract
  - [CLI instructions](./oracle-onchain/sep40/cli)
- Example on how to use the Oracle from a consumer contract (in Rust) calling using Python
  - [SEP-40 Consumer Price Up/Down](./oracle-onchain/sep40/examples/price_up_down)
- A Web-based app for interacting with the deployed contract (in JS React)
  - [Visit web app](https://bp-ventures.github.io/lightecho-stellar-oracle/)
  - [Web app source code](./docs/v2.html)
- A JS fiddle for testing and debugging the contract calls
  - [Visit JS fiddle](https://playcode.io/1594911)

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

#### Featured projects

Have a project that uses our Oracle? Feel free to share with us and we'll be happy to list it here!

---

https://lightecho.io

_Made by BP Ventures_
