**Python SDK for the Lightecho Stellar Oracle**

```
pip install lightecho_stellar_oracle
```

Example:
```
from lightecho_stellar_oracle import OracleClient
from stellar_sdk.keypair import Keypair

# This is for XLM as the base there will be an additional one for USD as the base
XLM_BASE_CONTRACT = 'CC2U4QX2U7HLDW5HMK3K5NREWVJMGD5GBTLZSEHHU3FQABSG2OTSPDV6'

oracle_client = OracleClient(
    contract_id=XLM_BASE_CONTRACT,
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

# this is 16 decimals so convert
result['price'] = result['price'] / 1e18

# Printing the updated result
print(result)

#RESULT
#{'price': 0.11, 'timestamp': 1698240296}
```

For more information see [https://github.com/bp-ventures/lightecho-stellar-oracle](https://github.com/bp-ventures/lightecho-stellar-oracle).
