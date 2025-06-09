"""
Example script demonstrating the usage of fmus-fintech with Ethereum.

This script shows how to create wallets, connect to Ethereum networks,
check balances, send transactions, and interact with smart contracts.
"""

import os
import time
from fmus_fintech import Wallet, Ethereum, EthereumContract

# ERC-20 Token ABI (minimal subset for demonstration)
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
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
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
    }
]

def create_or_load_wallet():
    """Create a new wallet or load an existing one."""
    wallet_file = "wallet.txt"

    if os.path.exists(wallet_file):
        # Load existing wallet
        with open(wallet_file, "r") as f:
            mnemonic = f.read().strip()
        print(f"Loaded existing wallet")
        return Wallet.from_mnemonic(mnemonic)
    else:
        # Create new wallet
        wallet = Wallet.create()

        # Save mnemonic for future use
        with open(wallet_file, "w") as f:
            f.write(wallet.mnemonic)

        print(f"Created new wallet")
        print(f"Mnemonic saved to {wallet_file}")

        return wallet

def main():
    """Run the example script."""
    # Create or load a wallet
    wallet = create_or_load_wallet()

    # Print wallet addresses for different chains
    eth_address = wallet.get_address_for_chain("ethereum")
    print(f"Ethereum address: {eth_address}")

    # Connect to Ethereum network (using Sepolia testnet for example)
    # In a real project, you would use your own Infura/Alchemy/etc. key
    eth = Ethereum(
        wallet=wallet,
        provider_url="https://sepolia.infura.io/v3/your-project-id",
        network="sepolia"
    )

    try:
        # Check connection
        connected = eth.connect()
        print(f"Connected to Ethereum: {connected}")

        if connected:
            # Get chain ID
            chain_id = eth.get_chain_id()
            print(f"Chain ID: {chain_id}")

            # Get current block number
            block_number = eth.get_block_number()
            print(f"Current block: {block_number}")

            # Check ETH balance
            balance = eth.balance()
            print(f"ETH balance: {balance}")

            # Note: The following operations require a funded wallet on the network

            # Example: Send ETH (uncomment to run)
            # recipient = "0xRecipientAddress"  # Replace with a real address
            # amount = 0.01  # In Ether
            # print(f"Sending {amount} ETH to {recipient}...")
            # tx_hash = eth.send(to=recipient, amount=amount)
            # print(f"Transaction sent: {tx_hash}")
            #
            # # Wait for confirmation
            # print("Waiting for confirmation...")
            # receipt = eth.wait_for_receipt(tx_hash)
            # print(f"Transaction confirmed in block {receipt.block_number}")
            # print(f"Gas used: {receipt.gas_used}")

            # Example: Interact with ERC-20 token (USDC on Sepolia)
            # Replace with a real token contract address
            token_address = "0xTokenAddress"

            print(f"Loading token contract at {token_address}...")
            token = EthereumContract(token_address, ERC20_ABI, eth)

            # Read token information
            try:
                name = token.read.name()
                symbol = token.read.symbol()
                decimals = token.read.decimals()
                print(f"Token: {name} ({symbol}), Decimals: {decimals}")

                # Get token balance
                token_balance = token.read.balanceOf(eth_address)
                print(f"Token balance: {token_balance / (10 ** decimals)} {symbol}")

                # Example: Transfer tokens (uncomment to run)
                # recipient = "0xRecipientAddress"  # Replace with a real address
                # amount = 10 * (10 ** decimals)  # 10 tokens with correct decimals
                # print(f"Sending {amount / (10 ** decimals)} {symbol} to {recipient}...")
                # tx_hash = token.write.transfer(recipient, amount)
                # print(f"Transaction sent: {tx_hash}")
                #
                # # Wait for confirmation
                # print("Waiting for confirmation...")
                # receipt = eth.wait_for_receipt(tx_hash)
                # print(f"Transaction confirmed in block {receipt.block_number}")

            except Exception as e:
                print(f"Error interacting with token: {e}")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Disconnect
        eth.disconnect()
        print("Disconnected from Ethereum")

if __name__ == "__main__":
    main()
