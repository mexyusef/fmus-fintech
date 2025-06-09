"""
fmus-fintech - A comprehensive Python library for Web3 and blockchain interactions.

This library provides a unified gateway to the decentralized financial ecosystem,
enabling developers to build sophisticated blockchain applications with minimal effort.
"""

__version__ = "0.0.1"

# Core components
from fmus_fintech.core.wallet import Wallet

# Chain implementations
from fmus_fintech.chains.ethereum import Ethereum

# Contract classes
from fmus_fintech.core.contract import Contract
from fmus_fintech.chains.ethereum_contract import EthereumContract

# Token standards
from fmus_fintech.chains.erc20 import ERC20Token, ERC20_ABI

# These will be imported as implementation progresses
# from fmus_fintech.chains.solana import Solana
# from fmus_fintech.chains.bitcoin import Bitcoin

# Plugin registration
_REGISTERED_CHAINS = {}

def register_chain(chain_name):
    """
    Decorator to register a custom chain implementation.

    Args:
        chain_name (str): The name of the chain to register.

    Returns:
        callable: Decorator function that registers the class.
    """
    def decorator(cls):
        _REGISTERED_CHAINS[chain_name] = cls
        return cls
    return decorator

def get_chain(chain_name):
    """
    Get a registered chain implementation by name.

    Args:
        chain_name (str): The name of the registered chain.

    Returns:
        class: The chain implementation class.

    Raises:
        ValueError: If the chain is not registered.
    """
    if chain_name not in _REGISTERED_CHAINS:
        raise ValueError(f"Chain '{chain_name}' is not registered")
    return _REGISTERED_CHAINS[chain_name]

# Register built-in chains
register_chain("ethereum")(Ethereum)
# More chains will be registered as they are implemented
