#!/bin/bash
# Example usage: ./deploy_contract.sh --contract-hex-path ./misc/registry.hex --private-key-path ./misc/private_key.txt --http-provider-url http://localhost:8545

# Function to display usage
usage() {
    echo "Usage: $0 --contract-hex-path <path_to_contract_hex> --private-key-path <path_to_private_key> [--http-provider-url <http_provider_url>]"
    exit 1
}

# Default HTTP provider URL
HTTP_PROVIDER="http://localhost:8545"

# Parse named arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --contract-hex-path) CONTRACT_HEX_PATH="$2"; shift ;;
        --private-key-path) PRIVATE_KEY_PATH="$2"; shift ;;
        --http-provider-url) HTTP_PROVIDER="$2"; shift ;;
        *) usage ;;
    esac
    shift
done

if [ -z "$CONTRACT_HEX_PATH" ]; then
    usage
fi

# Read the private key from the file
PRIVATE_KEY=$(cat "$PRIVATE_KEY_PATH")

# Get the block number at the start of the script
BLOCK_NUMBER=$(cast block-number --rpc-url $HTTP_PROVIDER)
echo "Block number at start of script: $BLOCK_NUMBER"

# Get the sender address using the private key
SENDER_ADDRESS=$(cast wallet address --private-key $PRIVATE_KEY)
echo "Sender address: $SENDER_ADDRESS"

# Get the balance of the sender address
BALANCE=$(cast balance $SENDER_ADDRESS --rpc-url $HTTP_PROVIDER)
echo "Balance at start of script: $BALANCE"

# Read or compile the contract code
if [ -n "$CONTRACT_HEX_PATH" ]; then
    # Read the contract code from the hex file
    CONTRACT_CODE=$(cat "$CONTRACT_HEX_PATH" | tr -d '\n')
fi

# Prepend 0x to the contract code
CONTRACT_CODE="0x$CONTRACT_CODE"

# Deploy the contract
RECEIPT=$(cast send --private-key $PRIVATE_KEY --rpc-url $HTTP_PROVIDER --create $CONTRACT_CODE)
TX_HASH=$(echo "$RECEIPT" | grep 'transactionHash' | awk '{print $2}')
CONTRACT_ADDRESS=$(echo "$RECEIPT" | grep 'contractAddress' | awk '{print $2}')
echo "Transaction hash: $TX_HASH"

# Wait for the transaction to be mined
while true; do
    RECEIPT=$(cast tx $TX_HASH --rpc-url $HTTP_PROVIDER)
    if [ "$RECEIPT" != "null" ]; then
        break
    fi
    sleep 1
done

# Get the block number at the end of the script
BLOCK_NUMBER=$(cast block-number --rpc-url $HTTP_PROVIDER)
echo "Block number at end of script: $BLOCK_NUMBER"

# Get the balance of the sender address
BALANCE=$(cast balance $SENDER_ADDRESS --rpc-url $HTTP_PROVIDER)
echo "Balance at end of script: $BALANCE"

# Echo the contract address
echo "Contract address: $CONTRACT_ADDRESS"
