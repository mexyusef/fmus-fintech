"""
Example script demonstrating the usage of fmus-fintech with ERC-20 tokens.

This script shows how to interact with ERC-20 tokens on the Ethereum network,
including checking balances, transfers, approvals, and events.
"""

import os
import json
import time
from fmus_fintech import Wallet, Ethereum, ERC20Token

# Load or create a wallet
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

def print_token_info(token):
    """Print basic information about an ERC-20 token."""
    print(f"Token: {token.name} ({token.symbol})")
    print(f"Decimals: {token.decimals}")
    print(f"Total Supply: {token.total_supply() / (10 ** token.decimals):,.2f} {token.symbol}")

def print_token_balance(token, address=None):
    """Print the token balance of an address."""
    if address:
        raw_balance = token.balance_of(address)
        formatted_balance = token.formatted_balance_of(address)
        print(f"Balance of {address}: {formatted_balance:,.2f} {token.symbol} ({raw_balance} raw units)")
    else:
        raw_balance = token.balance_of()
        formatted_balance = token.formatted_balance_of()
        print(f"Your balance: {formatted_balance:,.2f} {token.symbol} ({raw_balance} raw units)")

def handle_transfer_event(event):
    """Handle a token transfer event."""
    from_addr = event["args"].get("_from")
    to_addr = event["args"].get("_to")
    value = int(event["args"].get("_value", 0))

    print(f"Transfer: {from_addr} -> {to_addr}: {value}")

def main():
    """Run the example script."""
    # Create or load a wallet
    wallet = create_or_load_wallet()

    # Get Ethereum address from wallet
    eth_address = wallet.get_address_for_chain("ethereum")
    print(f"Ethereum address: {eth_address}")

    # Connect to Ethereum (using Sepolia testnet for example)
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

        if not connected:
            print("Failed to connect to Ethereum network")
            return

        # In a real example, you would use an actual token address
        # Here we're using the USDC contract address on Sepolia as an example
        token_address = "0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238"  # Example USDC address on Sepolia

        print(f"Loading ERC-20 token at {token_address}...")
        token = ERC20Token(token_address, eth)

        # Get token information
        try:
            print_token_info(token)
            print_token_balance(token)

            # Example: Get token balance of another address
            another_address = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"  # Example address
            print_token_balance(token, another_address)

            # Example: Check allowance
            spender = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"  # Example spender address
            allowance = token.allowance(eth_address, spender)
            print(f"Allowance for {spender}: {allowance / (10 ** token.decimals):,.2f} {token.symbol}")

            # The following operations require a funded wallet with tokens
            # They are commented out to prevent accidental execution

            # Example: Transfer tokens
            # recipient = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"  # Example recipient
            # amount = 1.0  # 1 token with correct decimals applied automatically
            # print(f"Sending {amount} {token.symbol} to {recipient}...")
            # tx_hash = token.transfer(recipient, amount)
            # print(f"Transaction sent: {tx_hash}")
            #
            # # Wait for confirmation
            # print("Waiting for confirmation...")
            # receipt = eth.wait_for_receipt(tx_hash)
            # print(f"Transaction confirmed in block {receipt.block_number}")

            # Example: Approve tokens for spending
            # spender = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"  # Example spender
            # amount = 10.0  # 10 tokens
            # print(f"Approving {amount} {token.symbol} for {spender}...")
            # tx_hash = token.approve(spender, amount)
            # print(f"Transaction sent: {tx_hash}")
            #
            # # Wait for confirmation
            # print("Waiting for confirmation...")
            # receipt = eth.wait_for_receipt(tx_hash)
            # print(f"Transaction confirmed in block {receipt.block_number}")

            # Example: Get token transfer history
            print("\nGetting recent token transfers...")
            transfers = token.get_token_transfers(eth_address, from_block=0)
            if transfers:
                print(f"Found {len(transfers)} transfers:")
                for transfer in transfers:
                    from_addr = transfer["args"].get("_from", "0x0")
                    to_addr = transfer["args"].get("_to", "0x0")
                    value = int(transfer["args"].get("_value", 0))
                    formatted_value = value / (10 ** token.decimals)

                    direction = "RECEIVED" if to_addr == eth_address else "SENT"
                    print(f"  {direction}: {formatted_value:,.2f} {token.symbol}")
                    print(f"    From: {from_addr}")
                    print(f"    To: {to_addr}")
                    print(f"    Block: {transfer['blockNumber']}")
                    print(f"    Tx Hash: {transfer['transactionHash']}")
                    print()
            else:
                print("No transfers found")

            # Example: Watch for token transfers (uncomment to run)
            # print("\nWatching for token transfers (press Ctrl+C to stop)...")
            # subscription_id = token.watch_transfers(handle_transfer_event, eth_address)
            #
            # try:
            #     # Keep the script running to receive events
            #     while True:
            #         time.sleep(1)
            # except KeyboardInterrupt:
            #     print("Stopping event watcher...")
            #     token.unwatch_transfers(subscription_id)

        except Exception as e:
            print(f"Error interacting with token: {e}")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Disconnect from the network
        eth.disconnect()
        print("Disconnected from Ethereum")

if __name__ == "__main__":
    main()
