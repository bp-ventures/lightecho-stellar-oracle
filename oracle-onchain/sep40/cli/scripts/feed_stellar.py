#!/usr/bin/env -S poetry run python
from decimal import Decimal
import requests
import pathlib
from subprocess import check_output
import sys


source_amount = "10"
params = {
    "source_asset_type": "native",
    "source_amount": source_amount,
    "destination_assets": "USDC:GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN",
}
url = "https://horizon.stellar.org/paths/strict-send"
print("fetching stellar strict send paths")
r = requests.get(url, params=params)
r.raise_for_status()
records = r.json()["_embedded"]["records"]
if not records:
    print("no paths found for XLM-USDC")
    sys.exit(1)
dest_amount = Decimal(records[0]["destination_amount"])
price = dest_amount / Decimal(source_amount)
price = round(price, 18)
cli_dir = pathlib.Path(__file__).parent.parent.resolve()
print(f"adding Stellar XLM-USDC price {price} to contract")
out = check_output(["./cli.py", "oracle", "add_price", "0", "other", "USD", str(price)], cwd=cli_dir)
print(out.decode())
