Lightecho Oracle - Oracle smart contract for Soroban

### Overview

This project is an Oracle implementation for the Soroban Smart Contracts platform.

For background and goals of the project, see [BPV - Blockchain Oracle](./blockchain_oracle.md).

This repository contains two different implementations: v1 and v2.

v1 is our first attempt to deploy and test an Oracle in Soroban. Once we got it
working, we began implementing v2.

v2 is our current contract implementation. It's in alpha-stage and under active
development. It aims to be 100% compatible with [SEP-40](https://github.com/stellar/stellar-protocol/blob/master/ecosystem/sep-0040.md),
and also contain extra features specific to our implementation.

### How to test it

We deployed both v1 and v2 to Stellar Futurenet, which are testable by
invoking the contract functions directly in the blockchain:

Deployed contract addresses:

- v1: `225bd2966e21977e99d0360d00663c41db77fe0d2b234b438b8b3eb425f9f22f`
- v2: `65e9f660742a626bfac85222953bb689345974520afea512f2a500fbc2b5f039`

To make it easy to test and use the contracts, we developed a CLI and a web app,
as described below.

#### v1

v1 has both a CLI and a web app for testing.

- [v1 CLI](./oracle-onchain/v1/cli)
- [v1 Web app](https://bp-ventures.github.io/lightecho-stellar-oracle/)

#### v2

v2 has a CLI for testing.

- [v2 CLI](./oracle-onchain/v2/cli)

### Source code

#### v1
