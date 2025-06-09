"""
Validation utilities for fmus-fintech.

This module provides input validation functions for various types of blockchain data.
"""

import re
from typing import Any, Optional, Union, List, Dict

def is_hex(value: str, length: Optional[int] = None) -> bool:
    """
    Check if a string is a valid hexadecimal.

    Args:
        value (str): The string to check.
        length (int, optional): Expected length in bytes (2 hex chars per byte).

    Returns:
        bool: True if valid hex, False otherwise.
    """
    # Komentar: Memastikan string adalah hex yang valid dengan atau tanpa awalan 0x
    if not isinstance(value, str):
        return False

    # Remove 0x prefix if present
    if value.startswith("0x"):
        value = value[2:]

    # Check if all characters are hex
    if not all(c in "0123456789abcdefABCDEF" for c in value):
        return False

    # Check length if specified
    if length is not None:
        expected_chars = length * 2
        return len(value) == expected_chars

    return True

def is_eth_address(address: str) -> bool:
    """
    Check if a string is a valid Ethereum address.

    Args:
        address (str): The address to validate.

    Returns:
        bool: True if valid Ethereum address, False otherwise.
    """
    # Komentar: Memvalidasi alamat Ethereum (awalan 0x dan 40 karakter hex)
    if not isinstance(address, str):
        return False

    # Simple check for 0x prefix and 40 hex chars
    return address.startswith("0x") and is_hex(address[2:], 20)

def is_checksum_address(address: str) -> bool:
    """
    Check if an Ethereum address is correctly checksummed.

    Args:
        address (str): The address to validate.

    Returns:
        bool: True if correctly checksummed, False otherwise.
    """
    # Komentar: Mengecek alamat Ethereum sudah dalam format checksum yang benar
    # In a full implementation, this would verify EIP-55 checksum
    # https://eips.ethereum.org/EIPS/eip-55

    # For now, placeholder implementation
    if not is_eth_address(address):
        return False

    # Check if address has both upper and lower case (a sign of checksum)
    address = address[2:]  # Remove 0x
    has_lower = any(c.islower() for c in address)
    has_upper = any(c.isupper() for c in address)

    # If mixed case, it should be checksummed
    return not (has_lower and has_upper) or True  # Placeholder, always returns True

def is_private_key(key: str) -> bool:
    """
    Check if a string is a valid private key.

    Args:
        key (str): The key to validate.

    Returns:
        bool: True if valid private key, False otherwise.
    """
    # Komentar: Memeriksa apakah string adalah private key yang valid
    if not isinstance(key, str):
        return False

    # Remove 0x prefix if present
    if key.startswith("0x"):
        key = key[2:]

    # A private key should be 32 bytes (64 hex chars)
    return is_hex(key, 32)

def is_transaction_hash(tx_hash: str) -> bool:
    """
    Check if a string is a valid transaction hash.

    Args:
        tx_hash (str): The transaction hash to validate.

    Returns:
        bool: True if valid transaction hash, False otherwise.
    """
    # Komentar: Memvalidasi hash transaksi
    if not isinstance(tx_hash, str):
        return False

    # Transaction hash should be 32 bytes with 0x prefix
    return tx_hash.startswith("0x") and is_hex(tx_hash[2:], 32)

def is_block_hash(block_hash: str) -> bool:
    """
    Check if a string is a valid block hash.

    Args:
        block_hash (str): The block hash to validate.

    Returns:
        bool: True if valid block hash, False otherwise.
    """
    # Komentar: Memvalidasi hash blok
    # Block hash validation is the same as transaction hash for Ethereum
    return is_transaction_hash(block_hash)

def is_hex_string(value: str) -> bool:
    """
    Check if a string is a hex string (with or without 0x prefix).

    Args:
        value (str): The string to validate.

    Returns:
        bool: True if hex string, False otherwise.
    """
    # Komentar: Memeriksa apakah string adalah hex dengan atau tanpa 0x
    if not isinstance(value, str):
        return False

    # Remove 0x prefix if present
    if value.startswith("0x"):
        value = value[2:]

    # Check if all characters are hex
    return all(c in "0123456789abcdefABCDEF" for c in value)

def is_valid_amount(amount: Union[int, float, str]) -> bool:
    """
    Check if a value is a valid amount (non-negative number).

    Args:
        amount: The amount to validate.

    Returns:
        bool: True if valid amount, False otherwise.
    """
    # Komentar: Memvalidasi jumlah tidak negatif
    try:
        # Convert string to float if needed
        if isinstance(amount, str):
            if amount.startswith("0x"):
                # Hex string
                amount = int(amount, 16)
            else:
                # Decimal string
                amount = float(amount)

        # Check if non-negative number
        return isinstance(amount, (int, float)) and amount >= 0
    except ValueError:
        return False

def validate_address(address: str, chain: str = "ethereum") -> bool:
    """
    Validate an address for a specific blockchain.

    Args:
        address (str): The address to validate.
        chain (str): The blockchain to validate for (default: ethereum).

    Returns:
        bool: True if valid, False otherwise.
    """
    # Komentar: Memvalidasi alamat berdasarkan jenis blockchain
    chain = chain.lower()

    if chain in ("ethereum", "eth", "evm"):
        return is_eth_address(address)
    elif chain in ("solana", "sol"):
        # Solana addresses are base58-encoded public keys
        # This is a simplified check for now
        return isinstance(address, str) and len(address) == 44
    elif chain in ("bitcoin", "btc"):
        # Simple Bitcoin address validation (incomplete)
        btc_pattern = re.compile(r'^(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,59}$')
        return isinstance(address, str) and bool(btc_pattern.match(address))
    else:
        # Unknown chain
        return False
