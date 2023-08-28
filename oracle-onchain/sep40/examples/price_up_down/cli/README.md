Create `local_settings.py`:

```
SOURCE_SECRET = "SBKEDTLZ6DACGUDTBL7O2LPTEW46KGVZUEXSQGEXCBE5KFKZGDCD4YWW"

RPC_SERVER_URL = "https://rpc-futurenet.stellar.org:443/"
CONTRACT_ID = "65e9f660742a626bfac85222953bb689345974520afea512f2a500fbc2b5f039"
NETWORK_PASSPHRASE = "Test SDF Future Network ; October 2022"
```

```
poetry install

./cli --help
```
