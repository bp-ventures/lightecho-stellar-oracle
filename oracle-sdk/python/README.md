**Python SDK for the Lightecho Stellar Oracle**

```
pip install lightecho_stellar_oracle
```

```
from lightecho_stellar_oracle import OracleClient

oracle_client = OracleClient(
    contract_id="CC2U4QX2U7HLDW5HMK3K5NREWVJMGD5GBTLZSEHHU3FQABSG2OTSPDV6",
    signer=Keypair.from_secret("SAES4O3NXUE2CPIB7YH3O5ROAONADPZRXOEYFC4JPLNY6STOBM2RYLGH"),
    network="testnet",
)

tx_id, result = oracle_client.lastprice("other", "USD")
print(tx_id)
print(result)
```

For more information see [https://github.com/bp-ventures/lightecho-stellar-oracle](https://github.com/bp-ventures/lightecho-stellar-oracle).
