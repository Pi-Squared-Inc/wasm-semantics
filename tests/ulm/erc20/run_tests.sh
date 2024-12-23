set -e

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
ROOT_DIR="$SCRIPT_DIR/../../.."

# change to root directory
cd "$ROOT_DIR"

./scripts/run-dev-ulm &> ulm.log &
sleep 1

./scripts/ulm-load-lang ./build/lib/libkwasm.so

tests/ulm/erc20/erc20_test.sh

tests/ulm/erc20/erc20_negative_test.sh

kill %1
