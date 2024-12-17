#!/usr/bin/python3
import sys
from pathlib import Path

from eth_account import Account
from web3 import Web3
from web3.middleware import SignAndSendRawMiddlewareBuilder

ABI_MAP = {
    'erc20': [
        {'type': 'function', 'name': 'decimals', 'inputs': [], 'outputs': ['uint8']},
        {'type': 'function', 'name': 'totalSupply', 'inputs': [], 'outputs': ['uint256']},
        {
            'type': 'function',
            'name': 'balanceOf',
            'inputs': [{'name': 'owner', 'type': 'address'}],
            'outputs': [{'name': '', 'type': 'uint256'}],
        },
        {
            'type': 'function',
            'name': 'transfer',
            'inputs': [{'name': 'to', 'type': 'address'}, {'name': 'value', 'type': 'uint256'}],
            'outputs': [{'name': '', 'type': 'bool'}],
        },
        {
            'type': 'function',
            'name': 'transferFrom',
            'inputs': [
                {'name': 'from', 'type': 'address'},
                {'name': 'to', 'type': 'address'},
                {'name': 'value', 'type': 'uint256'},
            ],
            'outputs': [{'name': '', 'type': 'bool'}],
        },
        {
            'type': 'function',
            'name': 'approve',
            'inputs': [{'name': 'spender', 'type': 'address'}, {'name': 'value', 'type': 'uint256'}],
            'outputs': [{'name': '', 'type': 'bool'}],
        },
        {
            'type': 'function',
            'name': 'allowance',
            'inputs': [{'name': 'owner', 'type': 'address'}, {'name': 'spender', 'type': 'address'}],
            'outputs': [{'name': '', 'type': 'uint256'}],
        },
        {
            'type': 'function',
            'name': 'mint',
            'inputs': [{'name': 'account', 'type': 'address'}, {'name': 'value', 'type': 'uint256'}],
            'outputs': [],
        },
    ]
}


def run_method(w3, contract, sender, eth, method, params):
    func = contract.functions[method](params)
    tx_hash = func.transact({'from': sender.address, 'value': eth})
    call_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return call_receipt


USAGE = 'call.py <node_url> <contract_abi> <contract_address> <sender_private_key_file> <eth> <method> [param...]'


def main():
    args = sys.argv[1:]
    if len(args) < 1:
        print(USAGE)
        sys.exit(1)
    (node_url, abi, contract_addr, sender_pk_file, eth, method), params = args[:4], args[4], args[5:]
    # get web3 instance
    w3 = Web3(Web3.HTTPProvider(node_url))
    # get contract
    contract = w3.eth.contract(address=contract_addr, abi=ABI_MAP[abi])
    # get sender
    pk = bytes.fromhex(Path(sender_pk_file).read_text().strip().removeprefix('0x'))
    sender = Account.from_key(pk)
    # add signer
    w3.middleware_onion.inject(SignAndSendRawMiddlewareBuilder.build(sender), layer=0)
    # run method
    run_method(w3, contract, sender, eth, method, params)


if __name__ == '__main__':
    main()