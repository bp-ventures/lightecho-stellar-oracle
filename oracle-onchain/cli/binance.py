#!/usr/bin/env -S poetry run python
import pandas as pd
import requests
import pathlib
from subprocess import check_output


def inv_str(price):
    inv = round(1 / float(price), 12)
    return str(inv)


filter_symbols = ["XLMUSDT", "XLMTRY", "XLMBTC", "XLMEUR"]
u = "https://api.binance.com/api/v3/ticker/24hr"
r = requests.get(u)
df = pd.DataFrame(r.json())
df2 = df[df.symbol.isin(filter_symbols)]
print("start binance")
cli_dir = pathlib.Path(__file__).parent.resolve()
for index, row in df2.iterrows():
    if row["symbol"] in ["XLMUSDT"]:
        out = check_output(["./cli.py", "set-rate", "USD", " ", "1", row["lastPrice"]], cwd=cli_dir)
        print(out)
        # proc = subprocess.Popen([cmd, "set-rate", "USDC", "GBBD47IF6LWK7P7MDEVSCWR7DPUWV3NY3DTQEVFL4NAT4AQH3ZLLFLA5", row['lastPrice'], "1"],
        #    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if row["symbol"] in ["XLMEUR"]:
        # proc = subprocess.Popen([cmd, "set-rate", "EURC", "GDBDEI3NV72XSORX7DNYMGRRNXAXF62RPTGGVEXM2RLXIUIUU5DNZWWH", row['lastPrice'], "1"],
        #    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        pass
