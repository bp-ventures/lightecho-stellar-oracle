This is a Python-based CLI that can be used as an utility to invoke the
Oracle contract.

Create `local_settings.py`:

```
SOURCE_SECRET = "SBKEDTLZ6DACGUDTBL7O2LPTEW46KGVZUEXSQGEXCBE5KFKZGDCD4YWW"
ADMIN_SECRET = "SDFWYGBNP5TW4MS7RY5D4FILT65R2IEPWGL34NY2TLSU4DC4BJNXUAMU"

ORACLE_CONTRACT_ID = "" # empty by default, but you must put the oracle contract id here later

RPC_URL="https://my-custom-rpc.mydomain.com"
NETWORK_PASSPHRASE="Test SDF Network ; September 2015"
HORIZON_URL="https://horizon-testnet.stellar.org"
ADD_PRICES_SUCCESS_HEARTBEAT_URL="https://sm.hetrixtools.net/hb/?s=..."

# Each asset must have a unique integer representation.
# You must NEVER change the integer value for a given asset, otherwise it might
# conflict with other asset with the same integer value.
# ALWAYS use new integer value for new assets, even if there are existing unused values.
ASSETS_TO_ASSET_U32 = {
    #("other", "ARST"): 0,
    #("other", "AUDD"): 1,
    ("other", "BRL"): 2,
    #("other", "BTC"): 3,
    #("other", "BTCLN"): 4,
    #("other", "CLPX"): 5,
    #("other", "ETH"): 6,
    ("other", "EUR"): 7,
    ("other", "EURC"): 8,
    #("other", "EURT"): 9,
    #("other", "GYEN"): 10,
    ("other", "IDRT"): 11,
    ("other", "KES"): 12,
    #("other", "KRW"): 13,
    ("other", "NGNT"): 14,
    #("other", "TRY"): 15,
    #("other", "TRYB"): 16,
    ("other", "TZS"): 17,
    #("other", "UPUSDT"): 18,
    ("other", "USD"): 19,
    ("other", "USDC"): 20,
    #("other", "USDT"): 21,
    ("other", "VOL30d"): 22,
    #("other", "XCHF"): 23,
    #("other", "XLM"): 24,
    #("other", "XSGD"): 25,
    #("other", "YUSDC"): 26,
    #("other", "ZAR"): 27,
    #("other", "yBTC"): 28,
    #("other", "yUSDC"): 29,
    ("other", "INR"): 30,
    ("other", "ARS"): 31,
    ("other", "NGN"): 32,
    ("other", "IDR"): 33,
}
```

```
poetry install

./cli --help
```
