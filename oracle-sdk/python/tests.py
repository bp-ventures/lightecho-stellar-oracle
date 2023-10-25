import unittest

from stellar_sdk import Keypair

from lightecho_stellar_oracle import OracleClient

CONTRACT_ID = "CC2U4QX2U7HLDW5HMK3K5NREWVJMGD5GBTLZSEHHU3FQABSG2OTSPDV6"
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
