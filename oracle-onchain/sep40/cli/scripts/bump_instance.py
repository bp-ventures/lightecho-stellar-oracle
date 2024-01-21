import logging
import subprocess
from pathlib import Path
from lightecho_stellar_oracle import TESTNET_CONTRACT_XLM, TESTNET_CONTRACT_USD

db_path = Path(__file__).parent.parent.parent.parent.resolve() / "api" / "db.sqlite3"
cli_dir = Path(__file__).parent.parent.resolve()

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s %(filename)s:%(lineno)d %(levelname)s] %(message)s'
)
logger = logging.getLogger('bump_instance.py')


def run_cli(cmd: str):
    return subprocess.check_output(
        f"./cli {cmd}", shell=True, text=True, cwd=cli_dir
    )

if __name__ == "__main__":
    cmd = f"--oracle-contract-id {TESTNET_CONTRACT_XLM} oracle bump_instance --ledgers-to-live 7884000"
    logger.info(f"cli.py {cmd}")
    output = run_cli(cmd)
    logger.info(output)
    #cmd = f"--oracle-contract-id {TESTNET_CONTRACT_USD} oracle bump_instance --ledgers-to-live 7884000"
    #logger.info(f"cli.py {cmd}")
    #output = run_cli(cmd)
    #logger.info(output)
