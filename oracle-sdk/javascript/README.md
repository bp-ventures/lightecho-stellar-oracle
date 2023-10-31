This is the JavaScript SDK for [BP Ventures Lightecho Stellar Oracle](https://github.com/bp-ventures/lightecho-stellar-oracle).

Example usage in Browser:

```
<script src="https://unpkg.com/lightecho_stellar_oracle@latest/dist/lightecho_stellar_oracle.min.js"></script>
<script>
    const client = OracleClient.newTestnetXlm(
      "SAES4O3NXUE2CPIB7YH3O5ROAONADPZRXOEYFC4JPLNY6STOBM2RYLGH",
      {
        baseFee: 50000,
      }
    );
    client
      .prices_by_source(1, "USD", "", 2)
      .then((result) => console.log(result))
      .catch((err) => console.error(err));
</script>
```

Example usage in Node.js:

```
npm install --save lightecho_stellar_oracle
```

```
#TODO
```
