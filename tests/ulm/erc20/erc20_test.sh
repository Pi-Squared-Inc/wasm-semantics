#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
ROOT_DIR="$SCRIPT_DIR/../../.."

# change to root directory
cd "$ROOT_DIR"

# re-execute script with poetry to get poetry script aliases
if [ -z ${IN_POETRY_SHELL:+x} ]; then
  export IN_POETRY_SHELL=1
  exec poetry -C pykwasm run bash "$SCRIPT_DIR/$(basename -- $0)"
fi

# generate some accounts
a1=$(mkacct)
a2=$(mkacct)
a3=$(mkacct)

# fund accounts
fund /dev/stdin <<< $a1
fund /dev/stdin <<< $a2
fund /dev/stdin <<< $a3

# deploy contract
contract=$(deploy build/erc20/erc20.bin http://localhost:8545 /dev/stdin <<< $a1)

# check decimals
decimals=$(call http://localhost:8545 erc20 $contract /dev/stdin 0 decimals <<< $a1)

# check total supply
supply=$(call http://localhost:8545 erc20 $contract /dev/stdin 0 totalSupply <<< $a1)


