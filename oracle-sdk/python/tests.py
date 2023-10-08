import unittest

from stellar_sdk import Keypair

from lightecho_stellar_oracle import OracleClient

CONTRACT_ID = "CDVM2DJWM2TFES7BSNZQZMAE36RSF5ICMR3ZPRBZHWZFZR7HL2AS7JT7"
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
        self.assertEqual(base, ['Other', 'XLM'])
