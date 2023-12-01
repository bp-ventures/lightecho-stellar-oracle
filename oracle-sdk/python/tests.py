import unittest

from stellar_sdk import Keypair

from lightecho_stellar_oracle import OracleClient, TESTNET_CONTRACT_XLM

CONTRACT_ID = TESTNET_CONTRACT_XLM
SECRET = "SAES4O3NXUE2CPIB7YH3O5ROAONADPZRXOEYFC4JPLNY6STOBM2RYLGH"


class OracleTests(unittest.TestCase):
    def setUp(self):
        self.client = OracleClient(
            contract_id=CONTRACT_ID,
            signer=Keypair.from_secret(SECRET),
            network="testnet",
        )

    def test_base(self):
        _, base = self.client.base()
        self.assertEqual(base, {"asset_type": "other", "asset": "XLM"})

    def test_prices_by_source(self):
        _, result = self.client.prices_by_source(0, "other", "USD", 1)
        self.assertEqual(len(result), 1)

    def test_has_admin(self):
        _, result = self.client.has_admin()
        self.assertEqual(result, True)

    def test_read_admin(self):
        _, admin_public_key = self.client.read_admin()
        self.assertIsInstance(admin_public_key, str)

    def test_sources(self):
        _, source_ids = self.client.sources()
        self.assertIsInstance(source_ids, list)

    def test_price_by_source(self):
        _, price = self.client.price_by_source(0, "other", "USD", 0)
        self.assertEqual(price, None)

    def test_lastprice_by_source(self):
        _, price = self.client.lastprice_by_source(0, "other", "USD")
        self.assertIsInstance(price["price"], str)  # type: ignore
        self.assertIsInstance(price["timestamp"], int)  # type: ignore

    def test_assets(self):
        _, assets = self.client.assets()
        for asset in assets:
            self.assertIn("asset_type", asset)
            self.assertIn("asset", asset)

    def test_decimals(self):
        _, decimals = self.client.decimals()
        self.assertIsInstance(decimals, int)

    def test_resolution(self):
        _, resolution = self.client.resolution()
        self.assertIsInstance(resolution, int)

    def test_price(self):
        _, price = self.client.price("other", "USD", 0)
        self.assertEqual(price, None)

    def test_prices(self):
        _, prices = self.client.prices("other", "USD", 5)
        self.assertGreater(len(prices), 0)

    def test_lastprice(self):
        _, price = self.client.lastprice("other", "USD")
        self.assertNotEqual(price, None)

    def test_get_all_prices(self):
        _, prices = self.client.get_all_prices()
        print(prices)
        self.assertGreater(len(prices.keys()), 0)
        self.assertGreater(len(prices.get(0).keys()), 0) # type: ignore
