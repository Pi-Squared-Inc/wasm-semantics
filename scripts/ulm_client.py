import os
import unittest

from eth_abi import decode, encode
from web3 import Web3
from web3.middleware import SignAndSendRawMiddlewareBuilder

class ulm_client:
    """Python interface to ULM"""

    def setUp(self):
        """Set up test environment with web3 connection and account details"""
        # Initialize web3 connection
        self.rpc_url = os.getenv("RPC_URL")
        self.web3 = Web3(Web3.HTTPProvider(self.rpc_url))

        # Set up test account
        self.test_account_private_key = os.getenv("TEST_ACCOUNT_PRIVATE_KEY")
        self.test_account = self.web3.eth.account.from_key(
            self.test_account_private_key
        )
        self.test_account_address = self.test_account.address

        # Get contract addresses from environment
        self.registry_address = os.getenv("REGISTRY_ADDRESS")
        self.wbtc_address = os.getenv("WBTC_ADDRESS")
        self.pi2_address = os.getenv("PI2_ADDRESS")
        self.usdc_address = os.getenv("USDC_ADDRESS")
        self.weth_address = os.getenv("WETH_ADDRESS")

        # Add middleware to automatically sign transactions
        self.web3.middleware_onion.inject(
            SignAndSendRawMiddlewareBuilder.build(self.test_account), layer=0
        )

    def function_selector(self, function_signature):
        """Calculate function selector from signature

        Args:
            function_signature: String of function name and parameters

        Returns:
            bytes: First 4 bytes of keccak hash of function signature
        """
        return self.web3.keccak(text=function_signature)[:4]

    def mint_token(self, token_address):
        # Mint
        mint_selector = self.function_selector("mint(address,uint256)")
        mint_data = encode(
            ["address", "uint256"],
            [self.test_account_address, 1000000000000000000000000],
        )  # 1,000,000 tokens
        mint_tx = self.web3.eth.send_transaction(
            {
                "from": self.test_account_address,
                "to": token_address,
                "data": mint_selector + mint_data,
            }
        )
        mint_tx_receipt = self.web3.eth.wait_for_transaction_receipt(mint_tx)
        self.assertEqual(mint_tx_receipt["status"], 1)

        # Verify balance
        get_token_balance_selector = self.function_selector("balanceOf(address)")
        get_token_balance_data = encode(["address"], [self.test_account_address])
        get_token_balance_result = self.web3.eth.call(
            {
                "to": token_address,
                "data": get_token_balance_selector + get_token_balance_data,
            }
        )
        token_a_balance = int.from_bytes(get_token_balance_result, "big")

        self.assertEqual(token_a_balance, 1000000000000000000000000)

    def approve_token(self, token_address):
        """Test approving spending of tokens"""
        # Approve token A
        approve_selector = self.function_selector("approve(address,uint256)")
        approve_data = encode(
            ["address", "uint256"], [token_address, 500000000000000000000000]
        )  # 500,000 tokens
        approve_token_tx = self.web3.eth.send_transaction(
            {
                "from": self.test_account_address,
                "to": token_address,
                "data": approve_selector + approve_data,
            }
        )
        approve_token_tx_receipt = self.web3.eth.wait_for_transaction_receipt(
            approve_token_tx
        )
        self.assertEqual(approve_token_tx_receipt["status"], 1)

        # Verify token A allowance
        allowance_selector = self.function_selector("allowance(address,address)")
        allowance_token_data = encode(
            ["address", "address"], [self.test_account_address, token_address]
        )
        allowance_token_result = self.web3.eth.call(
            {
                "to": token_address,
                "data": allowance_selector + allowance_token_data,
            }
        )
        token_allowance = int.from_bytes(allowance_token_result, "big")
        self.assertEqual(token_allowance, 500000000000000000000000)

    def check_token_identity(
        self, token_address, expected_name, expected_decimals, expected_symbol
    ):
        """Read token identity"""
        token_identity_selector = self.function_selector("name()")
        token_identity_data = encode([], [])
        token_identity_result = self.web3.eth.call(
            {
                "to": token_address,
                "data": token_identity_selector + token_identity_data,
            }
        )

        name = decode(["string"], token_identity_result)[0]
        self.assertEqual(name, expected_name)

        token_identity_selector = self.function_selector("decimals()")
        token_identity_data = encode([], [])
        token_identity_result = self.web3.eth.call(
            {
                "to": token_address,
                "data": token_identity_selector + token_identity_data,
            }
        )
        self.assertEqual(
            int.from_bytes(token_identity_result, "big"), expected_decimals
        )

        token_identity_selector = self.function_selector("symbol()")
        token_identity_data = encode([], [])
        token_identity_result = self.web3.eth.call(
            {
                "to": token_address,
                "data": token_identity_selector + token_identity_data,
            }
        )

        symbol = decode(["string"], token_identity_result)[0]
        self.assertEqual(symbol, expected_symbol)

    def test_02_mint_wbtc(self):
        """Test minting WBTC (Rust) to test account"""
        self.mint_token(self.wbtc_address)

    def test_03_mint_pi2(self):
        """Test minting PI2 (Simple) to test account"""
        self.mint_token(self.pi2_address)

    def test_04_mint_usdc(self):
        """Test minting USDC (Solidity) to test account"""
        self.mint_token(self.usdc_address)

    def test_05_mint_weth(self):
        """Test minting WETH (EVM) to test account"""
        # Mint
        mint_selector = self.function_selector("deposit()")
        mint_data = encode([], [])
        mint_tx = self.web3.eth.send_transaction(
            {
                "from": self.test_account_address,
                "to": self.weth_address,
                "data": mint_selector + mint_data,
                "value": 10000000000000000,
            }
        )
        mint_tx_receipt = self.web3.eth.wait_for_transaction_receipt(mint_tx)
        self.assertEqual(mint_tx_receipt["status"], 1)

        # Verify balance
        get_token_balance_selector = self.function_selector("balanceOf(address)")
        get_token_balance_data = encode(["address"], [self.test_account_address])
        get_token_balance_result = self.web3.eth.call(
            {
                "to": self.weth_address,
                "data": get_token_balance_selector + get_token_balance_data,
            }
        )
        token_a_balance = int.from_bytes(get_token_balance_result, "big")

        self.assertEqual(token_a_balance, 10000000000000000)

        get_eth_balance_result = self.web3.eth.get_balance(self.weth_address)
        self.assertEqual(get_eth_balance_result, 10000000000000000)

    def test_06_approve_wbtc(self):
        """Test approving spending of WBTC (Rust)"""
        self.approve_token(self.wbtc_address)

    def test_07_approve_pi2(self):
        """Test approving spending of PI2 (Simple)"""
        self.approve_token(self.pi2_address)

    def test_08_approve_usdc(self):
        """Test approving spending of USDC (Solidity)"""
        self.approve_token(self.usdc_address)

    def test_09_approve_weth(self):
        """Test approving spending of WETH (EVM)"""
        self.approve_token(self.weth_address)

    def test_10_wbtc_identity(self):
        """Test WBTC (Rust) identity"""
        self.check_token_identity(self.wbtc_address, "Wrapped Bitcoin", 18, "WBTC")

    def test_11_pi2_identity(self):
        """Test PI2 (Simple) identity"""
        self.check_token_identity(self.pi2_address, "Pi Squared", 18, "PI2")

    def test_12_usdc_identity(self):
        """Test USDC (Solidity) identity"""
        self.check_token_identity(self.usdc_address, "USD Coin", 18, "USDC")

    def test_13_weth_identity(self):
        """Test WETH (EVM) identity"""
        self.check_token_identity(self.weth_address, "Wrapped Ethereum", 18, "WETH")

if __name__ == "__main__":
    pass
