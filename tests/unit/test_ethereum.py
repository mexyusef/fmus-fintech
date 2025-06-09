"""
Unit tests for the Ethereum module.
"""

import unittest
from unittest.mock import patch, MagicMock
import json

from fmus_fintech.core.wallet import Wallet
from fmus_fintech.chains.ethereum import (
    Ethereum, EthereumTransaction, EthereumTransactionBuilder, EthereumTransactionManager
)
from fmus_fintech.chains.ethereum_contract import EthereumContract

class TestEthereumTransaction(unittest.TestCase):
    """Test cases for the EthereumTransaction class."""

    def test_init(self):
        """Test initializing a transaction."""
        tx = EthereumTransaction(
            to="0x1234567890123456789012345678901234567890",
            value=1000000000000000000,  # 1 ETH in wei
            gas_price=20000000000,  # 20 Gwei
            gas_limit=21000,
            data=b'',
            nonce=0,
            chain_id=1
        )

        self.assertEqual(tx.to, "0x1234567890123456789012345678901234567890")
        self.assertEqual(tx.value, 1000000000000000000)
        self.assertEqual(tx.gas_price, 20000000000)
        self.assertEqual(tx.gas_limit, 21000)
        self.assertEqual(tx.data, b'')
        self.assertEqual(tx.nonce, 0)
        self.assertEqual(tx.chain_id, 1)
        self.assertIsNone(tx.v)
        self.assertIsNone(tx.r)
        self.assertIsNone(tx.s)
        self.assertIsNone(tx._hash)

    def test_sign(self):
        """Test signing a transaction."""
        tx = EthereumTransaction(
            to="0x1234567890123456789012345678901234567890",
            value=1000000000000000000,
            chain_id=1
        )

        # Sign transaction with placeholder private key
        private_key = "0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
        signed_tx = tx.sign(private_key)

        # Verify that signature fields are set
        self.assertIsNotNone(signed_tx.v)
        self.assertIsNotNone(signed_tx.r)
        self.assertIsNotNone(signed_tx.s)
        self.assertIsNotNone(signed_tx._hash)

        # Verify that the returned object is the same as the original
        self.assertIs(signed_tx, tx)

    def test_serialize(self):
        """Test serializing a transaction."""
        tx = EthereumTransaction(
            to="0x1234567890123456789012345678901234567890",
            value=1000000000000000000,
            chain_id=1
        )

        # Try to serialize unsigned transaction
        with self.assertRaises(ValueError):
            tx.serialize()

        # Sign transaction
        private_key = "0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
        tx.sign(private_key)

        # Serialize signed transaction
        serialized = tx.serialize()
        self.assertTrue(serialized.startswith("0x"))

    def test_get_hash(self):
        """Test getting the transaction hash."""
        tx = EthereumTransaction(
            to="0x1234567890123456789012345678901234567890",
            value=1000000000000000000,
            chain_id=1
        )

        # Try to get hash of unsigned transaction
        with self.assertRaises(ValueError):
            tx.get_hash()

        # Sign transaction
        private_key = "0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
        tx.sign(private_key)

        # Get hash of signed transaction
        tx_hash = tx.get_hash()
        self.assertTrue(tx_hash.startswith("0x"))
        self.assertEqual(len(tx_hash), 66)  # 0x + 64 hex chars

class TestEthereumTransactionBuilder(unittest.TestCase):
    """Test cases for the EthereumTransactionBuilder class."""

    def test_init(self):
        """Test initializing a transaction builder."""
        builder = EthereumTransactionBuilder(chain_id=1)
        self.assertEqual(builder._chain_id, 1)
        self.assertIsNone(builder._to)
        self.assertEqual(builder._value, 0)
        self.assertIsNone(builder._data)
        self.assertIsNone(builder._fee)
        self.assertIsNone(builder._nonce)
        self.assertIsNone(builder._gas_price)
        self.assertIsNone(builder._gas_limit)
        self.assertEqual(builder._type, 0)  # Legacy transaction type

    def test_fluent_interface(self):
        """Test the fluent interface of the transaction builder."""
        builder = EthereumTransactionBuilder(chain_id=1)

        # Test method chaining
        result = builder.to("0x1234567890123456789012345678901234567890") \
            .value(1) \
            .data(b'hello') \
            .gas_price(20000000000) \
            .gas_limit(21000) \
            .nonce(0)

        # Verify that methods return self for chaining
        self.assertIs(result, builder)

        # Verify that the values are set correctly
        self.assertEqual(builder._to, "0x1234567890123456789012345678901234567890")
        self.assertEqual(builder._value, 1)
        self.assertEqual(builder._data, b'hello')
        self.assertEqual(builder._gas_price, 20000000000)
        self.assertEqual(builder._gas_limit, 21000)
        self.assertEqual(builder._nonce, 0)

    def test_eip1559_fee(self):
        """Test setting EIP-1559 fee parameters."""
        builder = EthereumTransactionBuilder(chain_id=1)

        # Set EIP-1559 fee parameters
        builder.eip1559_fee(
            max_fee_per_gas=30000000000,
            max_priority_fee_per_gas=2000000000
        )

        # Verify that the values are set correctly
        self.assertEqual(builder._type, 2)  # EIP-1559 transaction type
        self.assertEqual(builder._max_fee_per_gas, 30000000000)
        self.assertEqual(builder._max_priority_fee_per_gas, 2000000000)

    def test_build(self):
        """Test building a transaction."""
        builder = EthereumTransactionBuilder(chain_id=1)

        # Try to build a transaction without required parameters
        with self.assertRaises(ValueError):
            builder.build()

        # Set required parameters
        builder.to("0x1234567890123456789012345678901234567890") \
            .gas_price(20000000000)

        # Build transaction
        tx = builder.build()

        # Verify that the transaction has the correct parameters
        self.assertIsInstance(tx, EthereumTransaction)
        self.assertEqual(tx.to, "0x1234567890123456789012345678901234567890")
        self.assertEqual(tx.value, 0)
        self.assertEqual(tx.gas_price, 20000000000)
        self.assertEqual(tx.chain_id, 1)

class TestEthereum(unittest.TestCase):
    """Test cases for the Ethereum class."""

    def setUp(self):
        """Set up test fixtures."""
        self.wallet = Wallet.create()

        # Mock the provider
        self.provider_mock = MagicMock()
        self.provider_mock.is_connected.return_value = True
        self.provider_mock.request.return_value = {"result": "0x0"}

        # Create Ethereum instance with mocked provider
        self.eth = Ethereum(wallet=self.wallet, network="mainnet")
        self.eth._provider = self.provider_mock

    def test_init(self):
        """Test initializing Ethereum."""
        eth = Ethereum(wallet=self.wallet, network="mainnet")
        self.assertEqual(eth._wallet, self.wallet)
        self.assertEqual(eth._network, "mainnet")
        self.assertFalse(eth._connected)

        # Test with invalid network
        with self.assertRaises(ValueError):
            Ethereum(network="invalid_network")

    def test_connect(self):
        """Test connecting to Ethereum."""
        # Test successful connection
        connected = self.eth.connect()
        self.assertTrue(connected)
        self.assertTrue(self.eth._connected)

        # Test connection failure
        self.provider_mock.is_connected.return_value = False
        connected = self.eth.connect()
        self.assertFalse(connected)
        self.assertFalse(self.eth._connected)

    def test_get_chain_id(self):
        """Test getting the chain ID."""
        # Set up mock response
        self.provider_mock.request.return_value = {"result": "0x1"}

        # Get chain ID
        chain_id = self.eth.get_chain_id()

        # Verify that the chain ID is correct
        self.assertEqual(chain_id, 1)

        # Verify that the request was made correctly
        self.provider_mock.request.assert_called_with("eth_chainId")

    def test_get_balance(self):
        """Test getting the balance."""
        # Set up mock response
        self.provider_mock.request.return_value = {"result": "0xde0b6b3a7640000"}  # 1 ETH in wei

        # Get balance
        balance = self.eth.get_balance()

        # Verify that the balance is correct (1 ETH in wei)
        self.assertEqual(balance, 1000000000000000000)

        # Verify that the request was made correctly
        address = self.wallet.get_address_for_chain("ethereum")
        self.provider_mock.request.assert_called_with("eth_getBalance", [address, "latest"])

    def test_balance(self):
        """Test getting the balance in Ether."""
        # Set up mock response
        self.provider_mock.request.return_value = {"result": "0xde0b6b3a7640000"}  # 1 ETH in wei

        # Get balance
        balance = self.eth.balance()

        # Verify that the balance is correct (1 ETH)
        self.assertEqual(balance, 1.0)

    def test_send(self):
        """Test sending ETH."""
        # Set up mock transaction manager
        tx_manager_mock = MagicMock()
        tx_builder_mock = MagicMock()
        tx_mock = MagicMock()

        tx_manager_mock.create_transaction.return_value = tx_builder_mock
        tx_builder_mock.build.return_value = tx_mock
        tx_mock.sign.return_value = tx_mock
        tx_manager_mock.broadcast.return_value = "0x1234567890"

        self.eth._tx_manager = tx_manager_mock

        # Send ETH
        recipient = "0x1234567890123456789012345678901234567890"
        amount = 1.0  # 1 ETH
        tx_hash = self.eth.send(to=recipient, amount=amount)

        # Verify that the transaction was created correctly
        tx_builder_mock.to.assert_called_with(recipient)
        tx_builder_mock.value.assert_called_with(1000000000000000000)  # 1 ETH in wei

        # Verify that the transaction was signed and broadcast
        tx_mock.sign.assert_called_once()
        tx_manager_mock.broadcast.assert_called_with(tx_mock)

        # Verify that the transaction hash is correct
        self.assertEqual(tx_hash, "0x1234567890")

if __name__ == "__main__":
    unittest.main()
