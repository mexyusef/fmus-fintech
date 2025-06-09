"""
Unit tests for the wallet module.
"""

import unittest
from unittest.mock import patch
import hashlib

from fmus_fintech.core.wallet import Wallet

class TestWallet(unittest.TestCase):
    """Test cases for the Wallet class."""

    def test_create_wallet(self):
        """Test creating a new wallet."""
        wallet = Wallet.create()
        self.assertIsNotNone(wallet.address)
        self.assertIsNotNone(wallet.mnemonic)

    def test_from_mnemonic(self):
        """Test creating a wallet from a mnemonic."""
        mnemonic = "placeholder mnemonic for development"
        wallet = Wallet.from_mnemonic(mnemonic)
        self.assertEqual(wallet.mnemonic, mnemonic)
        expected_address = "0x" + hashlib.sha256(mnemonic.encode()).hexdigest()[:40]
        self.assertEqual(wallet.address, expected_address)

    def test_from_private_key(self):
        """Test creating a wallet from a private key."""
        private_key = "0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
        wallet = Wallet.from_private_key(private_key)
        self.assertEqual(wallet._private_key, private_key)
        expected_address = "0x" + hashlib.sha256(private_key.encode()).hexdigest()[:40]
        self.assertEqual(wallet.address, expected_address)

    def test_get_address_for_chain(self):
        """Test getting addresses for different chains."""
        wallet = Wallet.create()

        # Test Ethereum address
        eth_address = wallet.get_address_for_chain("ethereum")
        self.assertTrue(eth_address.startswith("0x"))

        # Test Solana address
        sol_address = wallet.get_address_for_chain("solana")
        self.assertEqual(len(sol_address), 64)  # SHA-256 hash length

        # Test Bitcoin address
        btc_address = wallet.get_address_for_chain("bitcoin")
        self.assertTrue(btc_address.startswith("bc1"))

        # Test invalid chain
        with self.assertRaises(ValueError):
            wallet.get_address_for_chain("invalid_chain")

    def test_sign_and_verify_message(self):
        """Test signing and verifying a message."""
        wallet = Wallet.create()
        message = "Hello, World!"
        signature = wallet.sign_message(message)
        self.assertTrue(wallet.verify_message(message, signature))
        self.assertFalse(wallet.verify_message("Different message", signature))

    def test_export_private_key(self):
        """Test exporting a private key."""
        private_key = "0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
        wallet = Wallet.from_private_key(private_key)
        exported = wallet.export_private_key()
        self.assertEqual(exported, private_key)

    def test_export_keystore(self):
        """Test exporting a keystore."""
        wallet = Wallet.create()
        keystore = wallet.export_keystore("password123")
        self.assertEqual(keystore["version"], 3)
        self.assertEqual(keystore["address"], wallet.get_address_for_chain("ethereum"))

    def test_init_invalid(self):
        """Test initializing with invalid parameters."""
        with self.assertRaises(ValueError):
            Wallet()

if __name__ == "__main__":
    unittest.main()
