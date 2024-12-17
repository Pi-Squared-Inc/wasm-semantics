#!/usr/bin/python3
import sys
from requests.exceptions import ConnectionError
from pathlib import Path

from eth_account import Account
from web3 import Web3
from web3.middleware import SignAndSendRawMiddlewareBuilder


def fund_acct(w3, addr):
    try:
        fund_tx_hash = w3.eth.send_transaction(
            {'from': w3.eth.accounts[0], 'to': addr, 'value': 1000000000000000000}
        )
        fund_tx_receipt = w3.eth.wait_for_transaction_receipt(fund_tx_hash)
    except (ConnectionError, ConnectionRefusedError):
        print("Failed to connect to node")
        sys.exit(1)
    return fund_tx_receipt


USAGE = 'fund_acct.py <address> [node_url]'


def main():
    args = sys.argv[1:]
    if len(args) < 1 or len(args) > 2:
        print(USAGE)
        sys.exit(1)
    addr = args[0]
    node_url = 'http://localhost:8545'
    if len(args) > 1:
        node_url = args[1]
    assert Web3.is_address(addr)
    w3 = Web3(Web3.HTTPProvider(node_url))
    fund_receipt = fund_acct(w3, addr)
    print(fund_receipt)


if __name__ == '__main__':
    main()
