#!/usr/bin/env bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR"

RED='\033[0;31m'
NC='\033[0m' # No Color

if [ $# -ne 4 ]; then
  >&2 printf "${RED}Missing arguments${NC}\n"
  >&2 echo "Usage: deploy.sh ADMIN BASE DECIMALS RESOLUTION"
  exit 1
fi

set -e

echo "➤ Building contract"
cargo build --target wasm32-unknown-unknown --release

echo -n "Enter source secret (your input will be hidden): "
read -s source_secret
echo ""

echo "➤ Deploying contract to Futurenet"
soroban contract deploy \
    --wasm target/wasm32-unknown-unknown/release/oracle.wasm \
    --source "$source_secret" \
    --rpc-url https://rpc-futurenet.stellar.org:443 \
    --network-passphrase 'Test SDF Future Network ; October 2022'


echo "➤ Installiing CLI dependencies"
cd ../cli
poetry install

echo "➤ Initializing contract"
./cli initialize "$@"

set +e
