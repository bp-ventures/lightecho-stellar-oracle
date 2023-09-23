#!/usr/bin/env -S poetry run python
import pandas as pd
import requests
import pathlib
from subprocess import check_output

filter_symbols = ["XLMUSDT", "XLMTRY", "XLMBTC", "XLMEUR", "XLMBRL"]
u = "https://api.binance.com/api/v3/ticker/24hr"
print("fetching binance ticker")
r = requests.get(u)
r.raise_for_status()
df = pd.DataFrame(r.json())
df2 = df[df.symbol.isin(filter_symbols)]
cli_dir = pathlib.Path(__file__).parent.parent.resolve()
for index, row in df2.iterrows():
    if row["symbol"] in ["XLMUSDT"]:
        print(f"adding Binance {row['symbol']} price {row['lastPrice']} to contract")
        out = check_output(["./cli.py", "oracle", "add_price", "1", "other", "USD", row["lastPrice"]], cwd=cli_dir)
        print(out.decode())
