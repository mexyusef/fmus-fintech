# fmus-fintech

## Overview

`fmus-fintech` aims to serve as a unified gateway to the decentralized financial ecosystem, enabling developers to build sophisticated blockchain applications with minimal effort.

## Installation

```bash
pip install fmus-fintech
```

## Quick Start

```python
from fmus_fintech import Wallet, Ethereum, Solana, Bitcoin

# Create a new wallet
new_wallet = Wallet.create()
print(f"New wallet address: {new_wallet.address}")
print(f"Backup your mnemonic: {new_wallet.mnemonic}")

# Load an existing wallet
wallet = Wallet.from_mnemonic("your twelve word mnemonic phrase here")

# Connect to networks
eth = Ethereum(wallet)
sol = Solana(wallet)
btc = Bitcoin(wallet)

# Check balances across chains
balances = {
    "ETH": eth.balance(),
    "SOL": sol.balance(),
    "BTC": btc.balance()
}
print(f"Current balances: {balances}")
```

## Documentation

Not created yet.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.