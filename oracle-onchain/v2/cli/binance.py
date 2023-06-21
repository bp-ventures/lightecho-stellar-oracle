#!/usr/bin/env -S poetry run python
import pandas as pd
import requests
import pathlib
from subprocess import check_output


def inv_str(price):
    inv = round(1 / float(price), 12)
    return str(inv)


filter_symbols = ["XLMUSDT", "XLMTRY", "XLMBTC", "XLMEUR", "XLMBRL"]
u = "https://api.binance.com/api/v3/ticker/24hr"
print("fetching binance ticker")
r = requests.get(u)
df = pd.DataFrame(r.json())
df2 = df[df.symbol.isin(filter_symbols)]
cli_dir = pathlib.Path(__file__).parent.resolve()
for index, row in df2.iterrows():
    if row["symbol"] in ["XLMUSDT"]:
        print(f"adding {row['symbol']} price {row['lastPrice']} to contract")
        out = check_output(["./cli.py", "add-price", "1", "other", "USD", row["lastPrice"]], cwd=cli_dir)
        print(out.decode())
