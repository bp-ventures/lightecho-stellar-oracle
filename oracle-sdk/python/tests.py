"""
These tests are meant to be run against an already deployed contract.
The tests assume some prices were already fed into the contract.
"""
import time
import unittest

from stellar_sdk import Keypair

from lightecho_stellar_oracle import OracleClient, TESTNET_CONTRACT_XLM

CONTRACT_ID = TESTNET_CONTRACT_XLM
SECRET = "SAES4O3NXUE2CPIB7YH3O5ROAONADPZRXOEYFC4JPLNY6STOBM2RYLGH"


class OracleTests(unittest.TestCase):
    """
    These tests are meant to be run against an already deployed contract.
    The tests assume some prices were already fed into the contract.
    """
    def setUp(self):
        self.client = OracleClient(
            contract_id=CONTRACT_ID,
            signer=Keypair.from_secret(SECRET),
            network="testnet",
        )

    def test_base(self):
        time.sleep(10)  # avoids TRY_AGAIN_LATER error
        _, base = self.client.base()
        self.assertEqual(base, {"asset_type": "other", "asset": "XLM"})

    def test_prices_by_source(self):
        time.sleep(10)  # avoids TRY_AGAIN_LATER error
        _, result = self.client.prices_by_source(0, "other", "USD", 1)
        self.assertEqual(len(result), 1)

    def test_read_admin(self):
        time.sleep(10)  # avoids TRY_AGAIN_LATER error
        _, admin_public_key = self.client.read_admin()
        self.assertIsInstance(admin_public_key, str)

    def test_sources(self):
        time.sleep(10)  # avoids TRY_AGAIN_LATER error
        _, source_ids = self.client.sources()
        self.assertIsInstance(source_ids, list)

    def test_price_by_source(self):
        time.sleep(10)  # avoids TRY_AGAIN_LATER error
        _, price = self.client.price_by_source(0, "other", "USD", 0)
        self.assertEqual(price, None)

    def test_lastprice_by_source(self):
        time.sleep(10)  # avoids TRY_AGAIN_LATER error
        _, price = self.client.lastprice_by_source(0, "other", "USD")
        self.assertIsInstance(price["price"], str)  # type: ignore
        self.assertIsInstance(price["timestamp"], int)  # type: ignore

    def test_assets(self):
        time.sleep(10)  # avoids TRY_AGAIN_LATER error
        _, assets = self.client.assets()
        for asset in assets:
            self.assertIn("asset_type", asset)
            self.assertIn("asset", asset)

    def test_decimals(self):
        time.sleep(10)  # avoids TRY_AGAIN_LATER error
        _, decimals = self.client.decimals()
        self.assertIsInstance(decimals, int)

    def test_resolution(self):
        time.sleep(10)  # avoids TRY_AGAIN_LATER error
        _, resolution = self.client.resolution()
        self.assertIsInstance(resolution, int)

    def test_price(self):
        time.sleep(10)  # avoids TRY_AGAIN_LATER error
        _, price = self.client.price("other", "USD", 0)
        self.assertEqual(price, None)

    def test_prices(self):
        time.sleep(10)  # avoids TRY_AGAIN_LATER error
        _, prices = self.client.prices("other", "USD", 5)
        self.assertGreater(len(prices), 0)

    def test_lastprice(self):
        time.sleep(10)  # avoids TRY_AGAIN_LATER error
        _, price = self.client.lastprice("other", "USD")
        self.assertNotEqual(price, None)
