"""
ERC-20 token implementation for fmus-fintech.

This module provides functionality for interacting with ERC-20 tokens on
Ethereum and other EVM-compatible blockchains.
"""

from typing import Optional, List, Dict, Any, Union, Tuple
import json

from fmus_fintech.chains.ethereum import Ethereum
from fmus_fintech.chains.ethereum_contract import EthereumContract
from fmus_fintech.utils.validation import is_eth_address

# Standard ERC-20 ABI with core functionality
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [],
        "name": "name",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "totalSupply",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [
            {"name": "_owner", "type": "address"},
            {"name": "_spender", "type": "address"}
        ],
        "name": "allowance",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_to", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_spender", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_from", "type": "address"},
            {"name": "_to", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "transferFrom",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "_from", "type": "address"},
            {"indexed": True, "name": "_to", "type": "address"},
            {"indexed": False, "name": "_value", "type": "uint256"}
        ],
        "name": "Transfer",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "_owner", "type": "address"},
            {"indexed": True, "name": "_spender", "type": "address"},
            {"indexed": False, "name": "_value", "type": "uint256"}
        ],
        "name": "Approval",
        "type": "event"
    }
]

class ERC20Token:
    """
    ERC-20 token implementation.

    This class provides a high-level interface for interacting with ERC-20 tokens.
    """

    def __init__(
        self,
        address: str,
        ethereum: Ethereum,
        abi: Optional[Union[List[Dict[str, Any]], str]] = None
    ):
        """
        Initialize an ERC-20 token.

        Args:
            address (str): The token contract address.
            ethereum (Ethereum): The Ethereum network.
            abi (list or str, optional): Custom ABI for the token. If not provided,
                the standard ERC-20 ABI is used.

        Raises:
            ValueError: If the address is invalid.
        """
        if not is_eth_address(address):
            raise ValueError(f"Invalid Ethereum address: {address}")

        self.address = address
        self.ethereum = ethereum

        # Use provided ABI or default ERC-20 ABI
        token_abi = abi or ERC20_ABI

        # Create contract instance
        self.contract = EthereumContract(address, token_abi, ethereum)

        # Cache for token metadata
        self._name = None
        self._symbol = None
        self._decimals = None

    @property
    def name(self) -> str:
        """
        Get the token name.

        Returns:
            str: The token name.

        Raises:
            Exception: If the name cannot be retrieved.
        """
        if self._name is None:
            self._name = self.contract.read.name()
        return self._name

    @property
    def symbol(self) -> str:
        """
        Get the token symbol.

        Returns:
            str: The token symbol.

        Raises:
            Exception: If the symbol cannot be retrieved.
        """
        if self._symbol is None:
            self._symbol = self.contract.read.symbol()
        return self._symbol

    @property
    def decimals(self) -> int:
        """
        Get the token decimals.

        Returns:
            int: The token decimals.

        Raises:
            Exception: If the decimals cannot be retrieved.
        """
        if self._decimals is None:
            self._decimals = self.contract.read.decimals()
        return self._decimals

    def total_supply(self) -> int:
        """
        Get the total supply of the token.

        Returns:
            int: The total supply in token units.

        Raises:
            Exception: If the total supply cannot be retrieved.
        """
        return self.contract.read.totalSupply()

    def balance_of(self, address: Optional[str] = None) -> int:
        """
        Get the token balance of an address.

        Args:
            address (str, optional): The address to get the balance for.
                If not provided, uses the wallet's address.

        Returns:
            int: The token balance in token units.

        Raises:
            ValueError: If no address is provided and no wallet is set.
            Exception: If the balance cannot be retrieved.
        """
        if address is None:
            if self.ethereum.wallet is None:
                raise ValueError("No address provided and no wallet is set")
            address = self.ethereum.wallet.get_address_for_chain("ethereum")

        return self.contract.read.balanceOf(address)

    def formatted_balance_of(self, address: Optional[str] = None) -> float:
        """
        Get the formatted token balance of an address.

        Args:
            address (str, optional): The address to get the balance for.
                If not provided, uses the wallet's address.

        Returns:
            float: The token balance in human-readable format.

        Raises:
            ValueError: If no address is provided and no wallet is set.
            Exception: If the balance cannot be retrieved.
        """
        balance = self.balance_of(address)
        return balance / (10 ** self.decimals)

    def allowance(self, owner: str, spender: str) -> int:
        """
        Get the amount of tokens that a spender is allowed to spend on behalf of an owner.

        Args:
            owner (str): The token owner address.
            spender (str): The spender address.

        Returns:
            int: The allowance in token units.

        Raises:
            Exception: If the allowance cannot be retrieved.
        """
        return self.contract.read.allowance(owner, spender)

    def transfer(
        self,
        to: str,
        amount: Union[int, float],
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None
    ) -> str:
        """
        Transfer tokens to an address.

        Args:
            to (str): Recipient address.
            amount (int or float): Amount of tokens to send.
                If int, treated as token units. If float, treated as human-readable amount.
            gas_limit (int, optional): Gas limit for the transaction.
            gas_price (int, optional): Gas price in wei.

        Returns:
            str: The transaction hash.

        Raises:
            ValueError: If the wallet is not set or parameters are invalid.
            Exception: If the transaction fails.
        """
        if not is_eth_address(to):
            raise ValueError(f"Invalid Ethereum address: {to}")

        # Convert human-readable amount to token units if a float is provided
        if isinstance(amount, float):
            amount = int(amount * (10 ** self.decimals))

        # Prepare transaction options
        tx_options = {}
        if gas_limit is not None:
            tx_options["gas"] = gas_limit

        if gas_price is not None:
            tx_options["gas_price"] = gas_price

        # Send transaction
        return self.contract.write.transfer(to, amount, **tx_options)

    def approve(
        self,
        spender: str,
        amount: Union[int, float],
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None
    ) -> str:
        """
        Approve a spender to spend tokens.

        Args:
            spender (str): Spender address.
            amount (int or float): Amount of tokens to approve.
                If int, treated as token units. If float, treated as human-readable amount.
            gas_limit (int, optional): Gas limit for the transaction.
            gas_price (int, optional): Gas price in wei.

        Returns:
            str: The transaction hash.

        Raises:
            ValueError: If the wallet is not set or parameters are invalid.
            Exception: If the transaction fails.
        """
        if not is_eth_address(spender):
            raise ValueError(f"Invalid Ethereum address: {spender}")

        # Convert human-readable amount to token units if a float is provided
        if isinstance(amount, float):
            amount = int(amount * (10 ** self.decimals))

        # Prepare transaction options
        tx_options = {}
        if gas_limit is not None:
            tx_options["gas"] = gas_limit

        if gas_price is not None:
            tx_options["gas_price"] = gas_price

        # Send transaction
        return self.contract.write.approve(spender, amount, **tx_options)

    def transfer_from(
        self,
        from_address: str,
        to_address: str,
        amount: Union[int, float],
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None
    ) -> str:
        """
        Transfer tokens from one address to another using an allowance.

        Args:
            from_address (str): Source address.
            to_address (str): Destination address.
            amount (int or float): Amount of tokens to transfer.
                If int, treated as token units. If float, treated as human-readable amount.
            gas_limit (int, optional): Gas limit for the transaction.
            gas_price (int, optional): Gas price in wei.

        Returns:
            str: The transaction hash.

        Raises:
            ValueError: If the wallet is not set or parameters are invalid.
            Exception: If the transaction fails.
        """
        if not is_eth_address(from_address):
            raise ValueError(f"Invalid source address: {from_address}")

        if not is_eth_address(to_address):
            raise ValueError(f"Invalid destination address: {to_address}")

        # Convert human-readable amount to token units if a float is provided
        if isinstance(amount, float):
            amount = int(amount * (10 ** self.decimals))

        # Prepare transaction options
        tx_options = {}
        if gas_limit is not None:
            tx_options["gas"] = gas_limit

        if gas_price is not None:
            tx_options["gas_price"] = gas_price

        # Send transaction
        return self.contract.write.transferFrom(from_address, to_address, amount, **tx_options)

    def get_token_transfers(
        self,
        address: Optional[str] = None,
        from_block: Union[int, str] = 0,
        to_block: Union[int, str] = "latest"
    ) -> List[Dict[str, Any]]:
        """
        Get token transfer events for an address.

        Args:
            address (str, optional): The address to get transfers for.
                If not provided, uses the wallet's address.
            from_block (int or str): The starting block.
            to_block (int or str): The ending block.

        Returns:
            list: The matching transfer events.

        Raises:
            ValueError: If no address is provided and no wallet is set.
            Exception: If the query fails.
        """
        if address is None:
            if self.ethereum.wallet is None:
                raise ValueError("No address provided and no wallet is set")
            address = self.ethereum.wallet.get_address_for_chain("ethereum")

        # Get Transfer events
        transfers = self.contract.get_events(
            "Transfer",
            from_block=from_block,
            to_block=to_block,
            filter_params={}
        )

        # Filter events by address
        filtered_transfers = []
        for transfer in transfers:
            if (transfer["args"].get("_from") == address or
                transfer["args"].get("_to") == address):
                filtered_transfers.append(transfer)

        return filtered_transfers

    def watch_transfers(
        self,
        callback: callable,
        address: Optional[str] = None
    ) -> int:
        """
        Watch for token transfers involving an address.

        Args:
            callback (callable): Function to call when a transfer occurs.
            address (str, optional): The address to watch.
                If not provided, watches all transfers.

        Returns:
            int: A subscription ID that can be used to stop watching.

        Raises:
            Exception: If the subscription fails.
        """
        # Create a filter callback
        def filter_callback(event):
            if address is None:
                # No filter, call callback for all transfers
                callback(event)
            elif (event["args"].get("_from") == address or
                  event["args"].get("_to") == address):
                # Filter by address
                callback(event)

        # Watch for Transfer events
        return self.contract.watch_event("Transfer", filter_callback)

    def unwatch_transfers(self, subscription_id: int) -> bool:
        """
        Stop watching for token transfers.

        Args:
            subscription_id (int): The subscription ID.

        Returns:
            bool: True if unsubscribed successfully, False otherwise.
        """
        return self.contract.unwatch_event(subscription_id)

    @classmethod
    def deploy(
        cls,
        ethereum: Ethereum,
        name: str,
        symbol: str,
        decimals: int,
        total_supply: Union[int, float],
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None
    ) -> "ERC20Token":
        """
        Deploy a new ERC-20 token contract.

        Args:
            ethereum (Ethereum): The Ethereum network.
            name (str): The token name.
            symbol (str): The token symbol.
            decimals (int): The token decimals.
            total_supply (int or float): The initial total supply.
                If int, treated as token units. If float, treated as human-readable amount.
            gas_limit (int, optional): Gas limit for the deployment.
            gas_price (int, optional): Gas price in wei.

        Returns:
            ERC20Token: The deployed token.

        Raises:
            ValueError: If parameters are invalid.
            Exception: If deployment fails.
        """
        # This is a placeholder. In a real implementation, this would:
        # 1. Use a standard ERC-20 contract bytecode or template
        # 2. Compile it or load it
        # 3. Deploy it with the provided parameters

        raise NotImplementedError("ERC-20 token deployment is not implemented yet")

    def __str__(self) -> str:
        """String representation of the token."""
        return f"{self.name} ({self.symbol})"

    def __repr__(self) -> str:
        """Developer representation of the token."""
        return f"ERC20Token(address='{self.address}', name='{self.name}', symbol='{self.symbol}')"
