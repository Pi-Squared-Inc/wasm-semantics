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
echo "Account1: $a1"

a2=$(mkacct)
echo "Account2: $a2"

a3=$(mkacct)
echo "Account3: $a3"


# fund accounts
echo "Funding account 1"
fund /dev/stdin <<< $a1

echo "Funding account 2"
fund /dev/stdin <<< $a2

echo "Funding account 3"
fund /dev/stdin <<< $a3

# deploy contract
echo "Deploying contract"
contract=$(deploy build/erc20/erc20.bin http://localhost:8545 /dev/stdin <<< $a1)
echo "Contract deployed. Contract address: $contract"

# check decimals
echo "Calling decimals on Account 1"
decimals=$(call http://localhost:8545 erc20 $contract /dev/stdin 0 decimals <<< $a1)
echo "Called decimals on Account 1. Result: $decimals"

# check total supply
echo "Calling supply on Account 1"
supply=$(call http://localhost:8545 erc20 $contract /dev/stdin 0 totalSupply <<< $a1)
echo "Called supply on Account 1. Result: $supply"
