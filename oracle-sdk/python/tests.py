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
        _, result = self.client.prices_by_source(1, "other", "USD", 1)
        self.assertEqual(len(result), 1)
