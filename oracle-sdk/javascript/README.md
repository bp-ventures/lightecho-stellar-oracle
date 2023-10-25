This is the JavaScript SDK for [BP Ventures Lightecho Stellar Oracle](https://github.com/bp-ventures/lightecho-stellar-oracle).

Example usage in Browser:

```
<script src="https://unpkg.com/lightecho_stellar_oracle@latest/dist/lightecho_stellar_oracle.min.js"></script>
<script>
  const client = new OracleClient(
    "CC2U4QX2U7HLDW5HMK3K5NREWVJMGD5GBTLZSEHHU3FQABSG2OTSPDV6",
    "https://soroban-testnet.stellar.org",
    "Test SDF Network ; September 2015",
    "SAES4O3NXUE2CPIB7YH3O5ROAONADPZRXOEYFC4JPLNY6STOBM2RYLGH",
    "https://lightecho-stellar-oracle-api.bpventures.us"
  );
  client
    .read_admin()
    .then((result) => console.log(result))
    .catch((err) => console.error(err));
</script>
```

Example usage in Node.js:

```
npm install --save lightecho_stellar_oracle
```

```

```
