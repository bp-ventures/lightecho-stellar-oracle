#!/usr/bin/env bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR"
cd ..

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

if [ $# -ne 4 ]; then
  >&2 printf "${RED}Missing arguments${NC}\n"
  >&2 echo "Usage: deploy.sh ADMIN BASE DECIMALS RESOLUTION"
  exit 1
fi

if ! command -v poetry &> /dev/null
then
  >&2 printf "${RED}poetry command not found. Visit https://python-poetry.org/ for installation instructions.${NC}\n"
  exit 1
fi

if [ -z $SOURCE_SECRET ]; then
  >&2 printf "${RED}Missing SOURCE_SECRET environment variable${NC}\n"
  exit 1
fi
export SOURCE_SECRET

set -e

echo "➤ Building contract"
make

echo "➤ Deploying contract to Futurenet"
contract_id=$(soroban contract deploy \
    --wasm target/wasm32-unknown-unknown/release/oracle.wasm \
    --source "$SOURCE_SECRET" \
    --rpc-url https://rpc-futurenet.stellar.org:443 \
    --network-passphrase 'Test SDF Future Network ; October 2022')

printf "${GREEN}Deployed contract ID: ${contract_id}${NC}\n"

echo "➤ Initializing contract"
cd "$SCRIPT_DIR"
poetry install
poetry run python initialize.py $contract_id "$@"

printf "${GREEN}Contract initialized successfully${NC}\n"
