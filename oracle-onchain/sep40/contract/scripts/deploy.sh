#!/usr/bin/env bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR"
cd ..

RED='\033[0;31m'
NC='\033[0m' # No Color

if [ $# -ne 2 ]; then
  echo "Usage: $0 <version> <network>"
  exit 1
fi

VERSION="$1"
NETWORK="$2"

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
make "${VERSION}"

echo "➤ Deploying contract to $NETWORK"
contract_id=$(soroban contract deploy \
    --wasm target/wasm32-unknown-unknown/release/oracle.wasm \
    --source "$SOURCE_SECRET" \
    --network "$NETWORK")

if [ -z "$contract_id" ]; then
    printf "${RED}Failed to deploy contract${NC}\n"
    exit 1
fi
printf "Deployed contract ID: ${contract_id}\n"
