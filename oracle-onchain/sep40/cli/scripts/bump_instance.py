import logging
import subprocess
import importlib.util
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone

db_path = Path(__file__).parent.parent.parent.parent.resolve() / "api" / "db.sqlite3"
cli_dir = Path(__file__).parent.parent.resolve()
timestamp_file = Path(__file__).parent / "last_executed.txt"

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
    format="[%(asctime)s %(filename)s:%(lineno)d %(levelname)s] %(message)s",
)
logger = logging.getLogger("bump_instance.py")


def run_cli(cmd: str):
    return subprocess.check_output(f"./cli {cmd}", shell=True, text=True, cwd=cli_dir)


def should_execute() -> bool:
    """Return True if the script should execute based on last UTC execution time.
    Raises an error if the timestamp file is invalid."""
    if not timestamp_file.exists():
        return True
    with timestamp_file.open("r") as f:
        try:
            last_run = datetime.fromisoformat(f.read().strip())
        except Exception as e:
            raise RuntimeError(
                f"Failed to parse timestamp file '{timestamp_file}': {e}"
            )
        if last_run.tzinfo is None:
            last_run = last_run.replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) - last_run > timedelta(days=182)


def update_timestamp():
    with timestamp_file.open("w") as f:
        f.write(datetime.now(timezone.utc).isoformat())


if __name__ == "__main__":
    try:
        if should_execute():
            cmd = f"--oracle-contract-id {local_settings.ORACLE_CONTRACT_ID} oracle bump_instance --ledgers-to-live 7884000"
            logger.info(f"cli.py {cmd}")
            output = run_cli(cmd)
            logger.info(output)
            update_timestamp()
        else:
            logger.info("Skipping execution: last run was within the last 6 months.")
    except Exception as e:
        logger.error(f"Script failed: {e}")
        raise
