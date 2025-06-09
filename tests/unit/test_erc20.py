"""
Unit tests for the ERC-20 token module.
"""

import unittest
from unittest.mock import patch, MagicMock, PropertyMock
import json

from fmus_fintech.core.wallet import Wallet
from fmus_fintech.chains.ethereum import Ethereum
from fmus_fintech.chains.ethereum_contract import EthereumContract
from fmus_fintech.chains.erc20 import ERC20Token, ERC20_ABI

class TestERC20Token(unittest.TestCase):
    """Test cases for the ERC20Token class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create wallet
        self.wallet = Wallet.create()
        self.eth_address = "0x1234567890123456789012345678901234567890"

        # Mock wallet method
        self.wallet.get_address_for_chain = MagicMock(return_value=self.eth_address)

        # Create Ethereum instance
        self.ethereum = Ethereum(wallet=self.wallet, network="mainnet")

        # Mock provider
        self.provider_mock = MagicMock()
        self.provider_mock.request.return_value = {"result": "0x0"}
        self.ethereum._provider = self.provider_mock

        # Mock EthereumContract class
        self.contract_mock = MagicMock(spec=EthereumContract)
        self.contract_mock.read = MagicMock()
        self.contract_mock.write = MagicMock()

        # Configure read mock methods
        self.contract_mock.read.name.return_value = "Test Token"
        self.contract_mock.read.symbol.return_value = "TEST"
        self.contract_mock.read.decimals.return_value = 18
        self.contract_mock.read.totalSupply.return_value = 1000000 * (10 ** 18)  # 1 million tokens
        self.contract_mock.read.balanceOf.return_value = 100 * (10 ** 18)  # 100 tokens
        self.contract_mock.read.allowance.return_value = 10 * (10 ** 18)  # 10 tokens

        # Configure write mock methods
        self.contract_mock.write.transfer.return_value = "0x" + "0" * 64
        self.contract_mock.write.approve.return_value = "0x" + "0" * 64
        self.contract_mock.write.transferFrom.return_value = "0x" + "0" * 64

        # Configure get_events method
        self.contract_mock.get_events.return_value = []

        # Configure watch_event method
        self.contract_mock.watch_event.return_value = 123

        # Configure unwatch_event method
        self.contract_mock.unwatch_event.return_value = True

        # Mock EthereumContract constructor
        self.original_ethereum_contract = EthereumContract
        EthereumContract = MagicMock(return_value=self.contract_mock)

        # Create token
        self.token_address = "0xabcdef0123456789abcdef0123456789abcdef01"
        self.token = ERC20Token(self.token_address, self.ethereum)

        # Restore EthereumContract
        EthereumContract = self.original_ethereum_contract

    def test_init(self):
        """Test initializing an ERC-20 token."""
        # Verify that the token was initialized correctly
        self.assertEqual(self.token.address, self.token_address)
        self.assertEqual(self.token.ethereum, self.ethereum)
        self.assertEqual(self.token.contract, self.contract_mock)

        # Test with invalid address
        with self.assertRaises(ValueError):
            ERC20Token("invalid_address", self.ethereum)

    def test_name(self):
        """Test getting the token name."""
        name = self.token.name
        self.assertEqual(name, "Test Token")
        self.contract_mock.read.name.assert_called_once()

        # Test caching
        name = self.token.name
        self.assertEqual(name, "Test Token")
        self.contract_mock.read.name.assert_called_once()  # Should not be called again

    def test_symbol(self):
        """Test getting the token symbol."""
        symbol = self.token.symbol
        self.assertEqual(symbol, "TEST")
        self.contract_mock.read.symbol.assert_called_once()

        # Test caching
        symbol = self.token.symbol
        self.assertEqual(symbol, "TEST")
        self.contract_mock.read.symbol.assert_called_once()  # Should not be called again

    def test_decimals(self):
        """Test getting the token decimals."""
        decimals = self.token.decimals
        self.assertEqual(decimals, 18)
        self.contract_mock.read.decimals.assert_called_once()

        # Test caching
        decimals = self.token.decimals
        self.assertEqual(decimals, 18)
        self.contract_mock.read.decimals.assert_called_once()  # Should not be called again

    def test_total_supply(self):
        """Test getting the total supply."""
        total_supply = self.token.total_supply()
        self.assertEqual(total_supply, 1000000 * (10 ** 18))
        self.contract_mock.read.totalSupply.assert_called_once()

    def test_balance_of(self):
        """Test getting the token balance."""
        # Test with specific address
        address = "0x0987654321098765432109876543210987654321"
        balance = self.token.balance_of(address)
        self.assertEqual(balance, 100 * (10 ** 18))
        self.contract_mock.read.balanceOf.assert_called_with(address)

        # Test with default address (from wallet)
        balance = self.token.balance_of()
        self.assertEqual(balance, 100 * (10 ** 18))
        self.contract_mock.read.balanceOf.assert_called_with(self.eth_address)

        # Test with no address and no wallet
        self.token.ethereum.wallet = None
        with self.assertRaises(ValueError):
            self.token.balance_of()

    def test_formatted_balance_of(self):
        """Test getting the formatted token balance."""
        # Test with specific address
        address = "0x0987654321098765432109876543210987654321"
        balance = self.token.formatted_balance_of(address)
        self.assertEqual(balance, 100.0)

        # Test with default address
        balance = self.token.formatted_balance_of()
        self.assertEqual(balance, 100.0)

    def test_allowance(self):
        """Test getting the token allowance."""
        owner = "0x1111111111111111111111111111111111111111"
        spender = "0x2222222222222222222222222222222222222222"

        allowance = self.token.allowance(owner, spender)
        self.assertEqual(allowance, 10 * (10 ** 18))
        self.contract_mock.read.allowance.assert_called_with(owner, spender)

    def test_transfer(self):
        """Test transferring tokens."""
        # Test with integer amount
        to_address = "0x0987654321098765432109876543210987654321"
        amount = 5 * (10 ** 18)  # 5 tokens in raw units

        tx_hash = self.token.transfer(to_address, amount)

        self.assertEqual(tx_hash, "0x" + "0" * 64)
        self.contract_mock.write.transfer.assert_called_with(to_address, amount)

        # Test with float amount
        to_address = "0x0987654321098765432109876543210987654321"
        amount_float = 5.0  # 5 tokens in human-readable format
        amount_raw = 5 * (10 ** 18)  # 5 tokens in raw units

        tx_hash = self.token.transfer(to_address, amount_float)

        self.assertEqual(tx_hash, "0x" + "0" * 64)
        self.contract_mock.write.transfer.assert_called_with(to_address, amount_raw)

        # Test with gas options
        to_address = "0x0987654321098765432109876543210987654321"
        amount = 5 * (10 ** 18)
        gas_limit = 100000
        gas_price = 10000000000

        tx_hash = self.token.transfer(to_address, amount, gas_limit=gas_limit, gas_price=gas_price)

        self.assertEqual(tx_hash, "0x" + "0" * 64)
        self.contract_mock.write.transfer.assert_called_with(
            to_address, amount, gas=gas_limit, gas_price=gas_price
        )

        # Test with invalid address
        with self.assertRaises(ValueError):
            self.token.transfer("invalid_address", amount)

    def test_approve(self):
        """Test approving tokens for spending."""
        # Test with integer amount
        spender = "0x0987654321098765432109876543210987654321"
        amount = 5 * (10 ** 18)  # 5 tokens in raw units

        tx_hash = self.token.approve(spender, amount)

        self.assertEqual(tx_hash, "0x" + "0" * 64)
        self.contract_mock.write.approve.assert_called_with(spender, amount)

        # Test with float amount
        spender = "0x0987654321098765432109876543210987654321"
        amount_float = 5.0  # 5 tokens in human-readable format
        amount_raw = 5 * (10 ** 18)  # 5 tokens in raw units

        tx_hash = self.token.approve(spender, amount_float)

        self.assertEqual(tx_hash, "0x" + "0" * 64)
        self.contract_mock.write.approve.assert_called_with(spender, amount_raw)

        # Test with gas options
        spender = "0x0987654321098765432109876543210987654321"
        amount = 5 * (10 ** 18)
        gas_limit = 100000
        gas_price = 10000000000

        tx_hash = self.token.approve(spender, amount, gas_limit=gas_limit, gas_price=gas_price)

        self.assertEqual(tx_hash, "0x" + "0" * 64)
        self.contract_mock.write.approve.assert_called_with(
            spender, amount, gas=gas_limit, gas_price=gas_price
        )

        # Test with invalid address
        with self.assertRaises(ValueError):
            self.token.approve("invalid_address", amount)

    def test_transfer_from(self):
        """Test transferring tokens from one address to another."""
        # Test with integer amount
        from_address = "0x1111111111111111111111111111111111111111"
        to_address = "0x2222222222222222222222222222222222222222"
        amount = 5 * (10 ** 18)  # 5 tokens in raw units

        tx_hash = self.token.transfer_from(from_address, to_address, amount)

        self.assertEqual(tx_hash, "0x" + "0" * 64)
        self.contract_mock.write.transferFrom.assert_called_with(from_address, to_address, amount)

        # Test with float amount
        from_address = "0x1111111111111111111111111111111111111111"
        to_address = "0x2222222222222222222222222222222222222222"
        amount_float = 5.0  # 5 tokens in human-readable format
        amount_raw = 5 * (10 ** 18)  # 5 tokens in raw units

        tx_hash = self.token.transfer_from(from_address, to_address, amount_float)

        self.assertEqual(tx_hash, "0x" + "0" * 64)
        self.contract_mock.write.transferFrom.assert_called_with(from_address, to_address, amount_raw)

        # Test with gas options
        from_address = "0x1111111111111111111111111111111111111111"
        to_address = "0x2222222222222222222222222222222222222222"
        amount = 5 * (10 ** 18)
        gas_limit = 100000
        gas_price = 10000000000

        tx_hash = self.token.transfer_from(
            from_address, to_address, amount, gas_limit=gas_limit, gas_price=gas_price
        )

        self.assertEqual(tx_hash, "0x" + "0" * 64)
        self.contract_mock.write.transferFrom.assert_called_with(
            from_address, to_address, amount, gas=gas_limit, gas_price=gas_price
        )

        # Test with invalid addresses
        with self.assertRaises(ValueError):
            self.token.transfer_from("invalid_address", to_address, amount)

        with self.assertRaises(ValueError):
            self.token.transfer_from(from_address, "invalid_address", amount)

    def test_get_token_transfers(self):
        """Test getting token transfer events."""
        # Mock transfer events
        self.contract_mock.get_events.return_value = [
            {
                "event": "Transfer",
                "args": {
                    "_from": "0x0000000000000000000000000000000000000000",
                    "_to": self.eth_address,
                    "_value": 100 * (10 ** 18)
                },
                "blockNumber": 12345,
                "transactionHash": "0x" + "1" * 64,
                "logIndex": 0
            },
            {
                "event": "Transfer",
                "args": {
                    "_from": self.eth_address,
                    "_to": "0x0987654321098765432109876543210987654321",
                    "_value": 50 * (10 ** 18)
                },
                "blockNumber": 12346,
                "transactionHash": "0x" + "2" * 64,
                "logIndex": 0
            }
        ]

        # Get transfers for specific address
        transfers = self.token.get_token_transfers(self.eth_address)

        self.assertEqual(len(transfers), 2)
        self.contract_mock.get_events.assert_called_with(
            "Transfer", from_block=0, to_block="latest", filter_params={}
        )

        # Get transfers for default address
        transfers = self.token.get_token_transfers()

        self.assertEqual(len(transfers), 2)

        # Test with no address and no wallet
        self.token.ethereum.wallet = None
        with self.assertRaises(ValueError):
            self.token.get_token_transfers()

    def test_watch_transfers(self):
        """Test watching for token transfers."""
        # Create a mock callback
        callback = MagicMock()

        # Watch transfers
        subscription_id = self.token.watch_transfers(callback)

        self.assertEqual(subscription_id, 123)
        self.contract_mock.watch_event.assert_called_once()

        # Verify that the filter callback was created
        event_name, filter_callback = self.contract_mock.watch_event.call_args[0]
        self.assertEqual(event_name, "Transfer")

        # Test unwatch
        result = self.token.unwatch_transfers(subscription_id)

        self.assertTrue(result)
        self.contract_mock.unwatch_event.assert_called_with(subscription_id)

    def test_string_representation(self):
        """Test string representation of the token."""
        token_str = str(self.token)
        token_repr = repr(self.token)

        self.assertEqual(token_str, "Test Token (TEST)")
        self.assertEqual(token_repr, f"ERC20Token(address='{self.token_address}', name='Test Token', symbol='TEST')")

if __name__ == "__main__":
    unittest.main()
