import logging
import subprocess
import importlib.util
import sys
from pathlib import Path

db_path = Path(__file__).parent.parent.parent.parent.resolve() / "api" / "db.sqlite3"
cli_dir = Path(__file__).parent.parent.resolve()

mod_spec = importlib.util.spec_from_file_location(
    "local_settings", Path(__file__).resolve().parent.parent / "local_settings.py"
)
assert mod_spec
local_settings = importlib.util.module_from_spec(mod_spec)
sys.modules["local_settings"] = local_settings
assert mod_spec.loader
mod_spec.loader.exec_module(local_settings)

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
    cmd = f"--oracle-contract-id {local_settings.ORACLE_CONTRACT_ID} oracle bump_instance --ledgers-to-live 7884000"
    logger.info(f"cli.py {cmd}")
    output = run_cli(cmd)
    logger.info(output)
    #cmd = f"--oracle-contract-id {TESTNET_CONTRACT_USD} oracle bump_instance --ledgers-to-live 7884000"
    #logger.info(f"cli.py {cmd}")
    #output = run_cli(cmd)
    #logger.info(output)
