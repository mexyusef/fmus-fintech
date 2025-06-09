"""
Transaction module for fmus-fintech.

This module provides functionality for creating, signing, and broadcasting
transactions across different blockchain networks.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Union, Tuple
from enum import Enum

class TransactionStatus(Enum):
    """Status of a blockchain transaction."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    UNKNOWN = "unknown"

class Transaction(ABC):
    """
    Abstract base class for blockchain transactions.

    This class provides a common interface for working with transactions
    across different blockchain networks.
    """

    @abstractmethod
    def sign(self, private_key: str) -> "Transaction":
        """
        Sign the transaction with a private key.

        Args:
            private_key (str): Private key to sign with.

        Returns:
            Transaction: The signed transaction (self).

        Raises:
            ValueError: If the transaction cannot be signed.
        """
        pass

    @abstractmethod
    def serialize(self) -> str:
        """
        Serialize the transaction for broadcasting.

        Returns:
            str: The serialized transaction.
        """
        pass

    @abstractmethod
    def get_hash(self) -> str:
        """
        Get the transaction hash.

        Returns:
            str: The transaction hash.

        Raises:
            ValueError: If the transaction is not signed.
        """
        pass

class TransactionReceipt:
    """
    Receipt for a confirmed blockchain transaction.

    This class provides details about a transaction that has been included
    in a block.
    """

    def __init__(
        self,
        transaction_hash: str,
        block_number: int,
        block_hash: str,
        status: bool,
        gas_used: int,
        logs: List[Dict[str, Any]] = None
    ):
        """
        Initialize a transaction receipt.

        Args:
            transaction_hash (str): Hash of the transaction.
            block_number (int): Block number where the transaction was included.
            block_hash (str): Hash of the block.
            status (bool): True if transaction succeeded, False if it failed.
            gas_used (int): Amount of gas used by the transaction.
            logs (list, optional): Event logs emitted by the transaction.
        """
        self.transaction_hash = transaction_hash
        self.block_number = block_number
        self.block_hash = block_hash
        self.status = status
        self.gas_used = gas_used
        self.logs = logs or []

    def __repr__(self) -> str:
        """Developer representation of the receipt."""
        return (
            f"TransactionReceipt(hash={self.transaction_hash}, "
            f"block={self.block_number}, status={'success' if self.status else 'failed'})"
        )

class TransactionBuilder:
    """
    Base class for building transactions.

    This class provides a fluent interface for constructing blockchain
    transactions with proper parameters.
    """

    def __init__(self, chain_id: int):
        """
        Initialize a transaction builder.

        Args:
            chain_id (int): Chain ID of the target network.
        """
        self._chain_id = chain_id
        self._to = None
        self._value = 0
        self._data = None
        self._fee = None
        self._nonce = None

    def to(self, address: str) -> "TransactionBuilder":
        """
        Set the recipient address.

        Args:
            address (str): Recipient address.

        Returns:
            TransactionBuilder: Self for chaining.
        """
        self._to = address
        return self

    def value(self, amount: Union[int, float]) -> "TransactionBuilder":
        """
        Set the transaction value.

        Args:
            amount (int or float): Amount of native currency to send.

        Returns:
            TransactionBuilder: Self for chaining.
        """
        self._value = amount
        return self

    def data(self, data: Union[str, bytes]) -> "TransactionBuilder":
        """
        Set the transaction data.

        Args:
            data (str or bytes): Transaction data (for contract interactions).

        Returns:
            TransactionBuilder: Self for chaining.
        """
        self._data = data
        return self

    def fee(self, fee: Dict[str, Any]) -> "TransactionBuilder":
        """
        Set the transaction fee.

        Args:
            fee (dict): Fee details appropriate for the chain.

        Returns:
            TransactionBuilder: Self for chaining.
        """
        self._fee = fee
        return self

    def nonce(self, nonce: int) -> "TransactionBuilder":
        """
        Set the transaction nonce.

        Args:
            nonce (int): Nonce value.

        Returns:
            TransactionBuilder: Self for chaining.
        """
        self._nonce = nonce
        return self

    @abstractmethod
    def build(self) -> Transaction:
        """
        Build the transaction.

        Returns:
            Transaction: The constructed transaction.

        Raises:
            ValueError: If required parameters are missing.
        """
        pass

class TransactionManager:
    """
    Manager for handling transactions on a blockchain.

    This class provides functionality for creating, signing, broadcasting,
    and monitoring transactions.
    """

    def __init__(self, network):
        """
        Initialize a transaction manager.

        Args:
            network: Network instance for the blockchain.
        """
        self._network = network
        self._pending_transactions = {}

    def create_transaction(self) -> TransactionBuilder:
        """
        Create a new transaction builder.

        Returns:
            TransactionBuilder: A transaction builder for this chain.
        """
        # Placeholder implementation - will be implemented in chain-specific subclasses
        return TransactionBuilder(0)

    def get_nonce(self, address: str) -> int:
        """
        Get the next nonce for an address.

        Args:
            address (str): The address to get the nonce for.

        Returns:
            int: The next nonce to use.

        Raises:
            Exception: If the nonce cannot be retrieved.
        """
        # Placeholder implementation - will be implemented in chain-specific subclasses
        return 0

    def estimate_fee(self, transaction: Transaction) -> Dict[str, Any]:
        """
        Estimate the fee for a transaction.

        Args:
            transaction (Transaction): The transaction to estimate the fee for.

        Returns:
            dict: Fee details appropriate for the chain.

        Raises:
            Exception: If the fee cannot be estimated.
        """
        # Placeholder implementation - will be implemented in chain-specific subclasses
        return {"gas_price": 20000000000, "gas_limit": 21000}

    def broadcast(self, transaction: Transaction) -> str:
        """
        Broadcast a transaction to the network.

        Args:
            transaction (Transaction): The signed transaction to broadcast.

        Returns:
            str: The transaction hash.

        Raises:
            ValueError: If the transaction is not signed.
            Exception: If the broadcast fails.
        """
        # Placeholder implementation - will be implemented in chain-specific subclasses
        tx_hash = transaction.get_hash()
        self._pending_transactions[tx_hash] = transaction
        return tx_hash

    def get_status(self, tx_hash: str) -> TransactionStatus:
        """
        Get the status of a transaction.

        Args:
            tx_hash (str): The transaction hash.

        Returns:
            TransactionStatus: The current status of the transaction.

        Raises:
            Exception: If the status cannot be retrieved.
        """
        # Placeholder implementation - will be implemented in chain-specific subclasses
        if tx_hash in self._pending_transactions:
            return TransactionStatus.PENDING
        return TransactionStatus.UNKNOWN

    def get_receipt(self, tx_hash: str) -> Optional[TransactionReceipt]:
        """
        Get the receipt for a transaction.

        Args:
            tx_hash (str): The transaction hash.

        Returns:
            TransactionReceipt or None: The receipt if available, None if not confirmed.

        Raises:
            Exception: If the receipt cannot be retrieved.
        """
        # Placeholder implementation - will be implemented in chain-specific subclasses
        return None

    def wait_for_receipt(self, tx_hash: str, timeout: int = 120, poll_interval: int = 1) -> TransactionReceipt:
        """
        Wait for a transaction to be confirmed.

        Args:
            tx_hash (str): The transaction hash.
            timeout (int, optional): Maximum time to wait in seconds.
            poll_interval (int, optional): Time between polls in seconds.

        Returns:
            TransactionReceipt: The transaction receipt.

        Raises:
            TimeoutError: If the transaction doesn't confirm within the timeout.
            Exception: If the receipt cannot be retrieved.
        """
        # Placeholder implementation - will be implemented in chain-specific subclasses
        # In a real implementation, this would poll for the receipt until it's available
        return TransactionReceipt(
            transaction_hash=tx_hash,
            block_number=12345678,
            block_hash="0x" + "00" * 32,
            status=True,
            gas_used=21000
        )
