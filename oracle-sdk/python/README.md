**Python SDK for the Lightecho Stellar Oracle**

```
pip install lightecho_stellar_oracle
```

Example:
```
from lightecho_stellar_oracle import OracleClient, TESTNET_CONTRACT_XLM
from stellar_sdk.keypair import Keypair

oracle_client = OracleClient(
    contract_id=TESTNET_CONTRACT_XLM,
    signer=Keypair.from_secret("SAES4O3NXUE2CPIB7YH3O5ROAONADPZRXOEYFC4JPLNY6STOBM2RYLGH"),
    network="testnet",
)
# list the assets
print(oracle_client.assets())

# show the base Currency
print(oracle_client.base())

# get the last price
tx_id, result = oracle_client.lastprice("other", "USD")
print(tx_id)
print(result)

# Printing the updated result
print(result)

#RESULT
#{'price': 0.11, 'timestamp': 1698240296}
```

For more information see [https://github.com/bp-ventures/lightecho-stellar-oracle](https://github.com/bp-ventures/lightecho-stellar-oracle).
