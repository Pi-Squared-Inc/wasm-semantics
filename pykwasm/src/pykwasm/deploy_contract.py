#!/usr/bin/python3
from web3 import Web3
from web3.middleware import SignAndSendRawMiddlewareBuilder

rust_token_hex = open('/mnt/data/pi-squared/wasm-semantics/tests/ulm/erc20/erc20.bin').read().rstrip()

w3 = Web3(Web3.HTTPProvider('http://localhost:8545'))
sender = w3.eth.account.create()
pk = w3.to_hex(sender.key)
print(sender.address)

tx_hash = w3.eth.send_transaction({'from': w3.eth.accounts[0],'to':sender.address,'value':1000000000000000000})
print('transfer eth tx hash:', tx_hash)
w3.eth.wait_for_transaction_receipt(tx_hash)

w3.middleware_onion.inject(SignAndSendRawMiddlewareBuilder.build(sender), layer=0)

deploy_token_tx = {
  'from': sender.address,
  'data': rust_token_hex,
  'to': '',
  'value': 0,
  'gas': 11000000,
  'maxFeePerGas': 2000000000,
  'maxPriorityFeePerGas': 1000000000,
}

tx_hash = w3.eth.send_transaction(deploy_token_tx)
print('deploy tx hash:', tx_hash)
receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print('deploy receipt:', receipt)
token_address = receipt['contractAddress']

