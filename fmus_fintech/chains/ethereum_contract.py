"""
Ethereum contract implementation for fmus-fintech.

This module provides Ethereum-specific contract functionality, including
ABI encoding/decoding, event handling, and deployment.
"""

import json
from typing import Optional, List, Dict, Any, Union, Callable, Tuple, TypeVar, Generic

from fmus_fintech.core.contract import Contract
from fmus_fintech.chains.ethereum import Ethereum, EthereumTransaction
from fmus_fintech.utils.validation import is_eth_address

class EthereumContract(Contract):
    """
    Ethereum smart contract implementation.

    This class provides Ethereum-specific contract functionality.
    """

    def __init__(
        self,
        address: str,
        abi: Union[List[Dict[str, Any]], str],
        ethereum: Ethereum,
        bytecode: Optional[str] = None
    ):
        """
        Initialize an Ethereum contract.

        Args:
            address (str): The contract address.
            abi (list or str): The contract ABI as a list or JSON string.
            ethereum (Ethereum): The Ethereum network.
            bytecode (str, optional): The contract bytecode.

        Raises:
            ValueError: If the address is invalid or the ABI is malformed.
        """
        if not is_eth_address(address):
            raise ValueError(f"Invalid Ethereum address: {address}")

        # Parse ABI if it's a string
        if isinstance(abi, str):
            try:
                abi = json.loads(abi)
            except json.JSONDecodeError:
                raise ValueError("Invalid ABI JSON")

        # Store the Ethereum instance
        self.ethereum = ethereum

        super().__init__(address, abi, ethereum.provider, bytecode)

    def _call_function(
        self, function_name: str, args: List[Any], outputs: List[Dict[str, str]]
    ) -> Any:
        """
        Call a read-only contract function.

        Args:
            function_name (str): The function name.
            args (list): The function arguments.
            outputs (list): The function output definitions.

        Returns:
            Any: The function result.

        Raises:
            Exception: If the call fails.
        """
        # In a full implementation, this would:
        # 1. Encode the function call using the ABI
        # 2. Send an eth_call RPC request
        # 3. Decode the response using the ABI

        # For now, we'll use a simplified placeholder implementation
        # Find the function definition in the ABI
        function_abi = None
        for item in self.abi:
            if item.get("type") == "function" and item.get("name") == function_name:
                function_abi = item
                break

        if function_abi is None:
            raise ValueError(f"Function {function_name} not found in ABI")

        # Build signature from function name and input types
        input_types = [inp.get("type", "") for inp in function_abi.get("inputs", [])]
        function_signature = f"{function_name}({','.join(input_types)})"
        function_selector = function_signature  # In reality, this would be the first 4 bytes of the keccak-256 hash

        # Encode arguments
        encoded_args = []
        for arg in args:
            encoded_args.append(str(arg))

        # Create call object
        call_object = {
            "to": self.address,
            "data": function_selector + "".join(encoded_args)
        }

        # Make the call
        try:
            response = self.provider.request(
                "eth_call", [call_object, "latest"]
            )

            # Decode the response
            result = response["result"]

            # Simulate different return values based on outputs
            if not outputs:
                return None
            elif len(outputs) == 1:
                # Single output, return directly
                output_type = outputs[0]["type"]
                if output_type.startswith("uint"):
                    return int(result, 16) if result != "0x" else 0
                elif output_type == "string":
                    return result  # Simplified - would normally decode string
                elif output_type == "bool":
                    return result != "0x" and result != "0x0"
                elif output_type == "address":
                    return "0x" + result[2:].rjust(40, "0")
                else:
                    return result
            else:
                # Multiple outputs, return as tuple
                # Simplified - would normally decode tuple
                return tuple(result for _ in outputs)

        except Exception as e:
            raise Exception(f"Failed to call function {function_name}: {e}")

    def _transact_function(
        self, function_name: str, args: List[Any], tx_options: Dict[str, Any]
    ) -> str:
        """
        Call a contract function that requires a transaction.

        Args:
            function_name (str): The function name.
            args (list): The function arguments.
            tx_options (dict): Transaction options.

        Returns:
            str: The transaction hash.

        Raises:
            Exception: If the transaction fails.
        """
        if self.ethereum.wallet is None:
            raise ValueError("No wallet set")

        # Get function ABI
        function_abi = None
        for item in self.abi:
            if item.get("type") == "function" and item.get("name") == function_name:
                function_abi = item
                break

        if function_abi is None:
            raise ValueError(f"Function {function_name} not found in ABI")

        # In a full implementation, this would:
        # 1. Encode the function call using the ABI
        # 2. Create and sign a transaction
        # 3. Send the transaction

        # Build signature from function name and input types
        input_types = [inp.get("type", "") for inp in function_abi.get("inputs", [])]
        function_signature = f"{function_name}({','.join(input_types)})"
        function_selector = function_signature  # In reality, this would be the first 4 bytes of the keccak-256 hash

        # Encode arguments
        encoded_args = []
        for arg in args:
            encoded_args.append(str(arg))

        # Get sender address
        from_address = self.ethereum.wallet.get_address_for_chain("ethereum")

        # Create transaction data
        data = function_selector + "".join(encoded_args)

        # Create transaction builder
        tx_builder = self.ethereum.transaction_manager.create_transaction()
        tx_builder.to(self.address).data(data)

        # Set value if provided
        if "value" in tx_options:
            tx_builder.value(tx_options["value"])

        # Set gas limit if provided
        if "gas" in tx_options:
            tx_builder.gas_limit(tx_options["gas"])

        # Set gas price if provided
        if "gas_price" in tx_options:
            tx_builder.gas_price(tx_options["gas_price"])

        # Set nonce if provided
        if "nonce" in tx_options:
            tx_builder.nonce(tx_options["nonce"])

        # Get the private key from the wallet
        private_key = self.ethereum.wallet.export_private_key(chain="ethereum")

        # Build, sign, and broadcast the transaction
        transaction = tx_builder.build()
        transaction.sign(private_key)
        return self.ethereum.transaction_manager.broadcast(transaction)

    def parse_event_log(self, log: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse an Ethereum event log entry.

        Args:
            log (dict): The log entry to parse.

        Returns:
            dict: The parsed event data.

        Raises:
            ValueError: If the log cannot be parsed.
        """
        # In a full implementation, this would:
        # 1. Find the event in the ABI based on the topic
        # 2. Decode the data according to the event ABI

        # For now, we'll use a simplified placeholder implementation
        topics = log.get("topics", [])
        if not topics:
            raise ValueError("Log has no topics")

        # Try to find the event based on the first topic
        event_name = None
        event_abi = None
        for item in self.abi:
            if item.get("type") == "event":
                # In a real implementation, this would compare the hash of the event signature
                # with the first topic
                if item.get("name", "").lower() in topics[0].lower():
                    event_name = item.get("name")
                    event_abi = item
                    break

        if event_name is None:
            # Unknown event
            return {
                "event": "UnknownEvent",
                "args": {},
                "blockNumber": int(log.get("blockNumber", "0x0"), 16),
                "transactionHash": log.get("transactionHash", "0x" + "0" * 64),
                "logIndex": int(log.get("logIndex", "0x0"), 16)
            }

        # Decode event data
        # Simplified - would normally decode data
        return {
            "event": event_name,
            "args": {"arg1": "value1"},
            "blockNumber": int(log.get("blockNumber", "0x0"), 16),
            "transactionHash": log.get("transactionHash", "0x" + "0" * 64),
            "logIndex": int(log.get("logIndex", "0x0"), 16)
        }

    @classmethod
    def deploy(
        cls,
        abi: Union[List[Dict[str, Any]], str],
        bytecode: str,
        ethereum: Ethereum,
        *args,
        **kwargs
    ) -> "EthereumContract":
        """
        Deploy a new Ethereum contract.

        Args:
            abi (list or str): The contract ABI as a list or JSON string.
            bytecode (str): The contract bytecode.
            ethereum (Ethereum): The Ethereum network.
            *args: Arguments for the contract constructor.
            **kwargs: Transaction options.

        Returns:
            EthereumContract: The deployed contract.

        Raises:
            Exception: If deployment fails.
        """
        if ethereum.wallet is None:
            raise ValueError("No wallet set")

        # Parse ABI if it's a string
        if isinstance(abi, str):
            try:
                abi_list = json.loads(abi)
            except json.JSONDecodeError:
                raise ValueError("Invalid ABI JSON")
        else:
            abi_list = abi

        # Find constructor ABI
        constructor_abi = None
        for item in abi_list:
            if item.get("type") == "constructor":
                constructor_abi = item
                break

        # In a full implementation, this would:
        # 1. Encode the constructor arguments
        # 2. Append them to the bytecode
        # 3. Deploy the contract

        # For now, we'll use a simplified placeholder implementation
        data = bytecode

        # Get sender address
        from_address = ethereum.wallet.get_address_for_chain("ethereum")

        # Create transaction builder
        tx_builder = ethereum.transaction_manager.create_transaction()
        tx_builder.data(data)  # No 'to' address for contract deployment

        # Set gas limit if provided
        if "gas" in kwargs:
            tx_builder.gas_limit(kwargs["gas"])

        # Set gas price if provided
        if "gas_price" in kwargs:
            tx_builder.gas_price(kwargs["gas_price"])

        # Set nonce if provided
        if "nonce" in kwargs:
            tx_builder.nonce(kwargs["nonce"])

        # Get the private key from the wallet
        private_key = ethereum.wallet.export_private_key(chain="ethereum")

        # Build, sign, and broadcast the transaction
        transaction = tx_builder.build()
        transaction.sign(private_key)
        tx_hash = ethereum.transaction_manager.broadcast(transaction)

        # Wait for the transaction to be mined
        receipt = ethereum.wait_for_receipt(tx_hash)

        # Get the contract address from the receipt
        if not receipt.status:
            raise Exception("Contract deployment failed")

        # In a real implementation, this would get the contract address from the receipt
        # For now, we'll use a placeholder address
        contract_address = "0x" + "0" * 40

        return cls(contract_address, abi_list, ethereum, bytecode)

    def get_events(
        self,
        event_name: str,
        from_block: Union[int, str] = 0,
        to_block: Union[int, str] = "latest",
        filter_params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get events emitted by the contract.

        Args:
            event_name (str): The name of the event to get.
            from_block (int or str): The starting block.
            to_block (int or str): The ending block.
            filter_params (dict, optional): Additional filter parameters.

        Returns:
            list: The matching events.

        Raises:
            ValueError: If the event doesn't exist.
            Exception: If the query fails.
        """
        # Find the event ABI
        event_abi = None
        for item in self.abi:
            if item.get("type") == "event" and item.get("name") == event_name:
                event_abi = item
                break

        if event_abi is None:
            raise ValueError(f"Event {event_name} not found in ABI")

        # In a full implementation, this would:
        # 1. Create the event signature
        # 2. Hash it to get the topic
        # 3. Build the filter object
        # 4. Call eth_getLogs
        # 5. Parse the logs

        # For now, we'll use a simplified placeholder implementation
        filter_params = filter_params or {}

        # Create filter
        filter_obj = {
            "address": self.address,
            "fromBlock": hex(from_block) if isinstance(from_block, int) else from_block,
            "toBlock": hex(to_block) if isinstance(to_block, int) else to_block,
            "topics": []
        }

        try:
            response = self.provider.request("eth_getLogs", [filter_obj])
            logs = response["result"]

            # Parse each log
            parsed_logs = []
            for log in logs:
                try:
                    parsed_log = self.parse_event_log(log)
                    if parsed_log["event"] == event_name:
                        parsed_logs.append(parsed_log)
                except ValueError:
                    continue

            return parsed_logs

        except Exception as e:
            raise Exception(f"Failed to get events: {e}")

    def watch_event(
        self,
        event_name: str,
        callback: Callable[[Dict[str, Any]], None],
        filter_params: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Watch for new events emitted by the contract.

        Args:
            event_name (str): The name of the event to watch.
            callback (callable): Function to call when an event is received.
            filter_params (dict, optional): Additional filter parameters.

        Returns:
            int: A subscription ID that can be used to unsubscribe.

        Raises:
            ValueError: If the event doesn't exist.
            Exception: If the subscription fails.
        """
        # Find the event ABI
        event_abi = None
        for item in self.abi:
            if item.get("type") == "event" and item.get("name") == event_name:
                event_abi = item
                break

        if event_abi is None:
            raise ValueError(f"Event {event_name} not found in ABI")

        # In a full implementation, this would:
        # 1. Check if the provider supports subscriptions (WebSocket)
        # 2. Create the event signature
        # 3. Hash it to get the topic
        # 4. Create a subscription
        # 5. Set up a callback to parse logs and call the user's callback

        # For now, we'll use a simplified placeholder implementation
        filter_params = filter_params or {}

        # Create filter
        filter_obj = {
            "address": self.address,
            "topics": []
        }

        try:
            if not hasattr(self.provider, "subscribe"):
                raise ValueError("Provider does not support subscriptions")

            # Create wrapper callback to parse logs
            def wrapper_callback(log):
                try:
                    parsed_log = self.parse_event_log(log)
                    if parsed_log["event"] == event_name:
                        callback(parsed_log)
                except ValueError:
                    pass

            # Subscribe to logs
            return self.provider.subscribe("logs", wrapper_callback)

        except Exception as e:
            raise Exception(f"Failed to watch events: {e}")

    def unwatch_event(self, subscription_id: int) -> bool:
        """
        Stop watching for events.

        Args:
            subscription_id (int): The subscription ID.

        Returns:
            bool: True if unsubscribed successfully, False otherwise.
        """
        try:
            if not hasattr(self.provider, "unsubscribe"):
                raise ValueError("Provider does not support subscriptions")

            return self.provider.unsubscribe(subscription_id)

        except Exception as e:
            raise Exception(f"Failed to unwatch events: {e}")
