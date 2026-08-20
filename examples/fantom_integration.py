#!/usr/bin/env python3
"""
Fantom Blockchain RPC Client and Utilities Example.
Exposes tools for smart contract interactions, gas estimation, log parsing,
and transaction preparation.
"""

import httpx
import sys

# Official Fantom Opera Mainnet and Testnet public RPC endpoints
FANTOM_MAINNET_RPC = "https://rpc.ankr.com/fantom/"
FANTOM_TESTNET_RPC = "https://rpc.ankr.com/fantom_testnet/"

class FantomClient:
    def __init__(self, rpc_url: str = FANTOM_MAINNET_RPC):
        self.rpc_url = rpc_url
        self.headers = {"Content-Type": "application/json"}

    def _call_rpc(self, method: str, params: list) -> dict:
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1
        }
        with httpx.Client() as client:
            response = client.post(self.rpc_url, json=payload, headers=self.headers)
            response.raise_for_status()
            res_json = response.json()
            if "error" in res_json:
                raise Exception(f"RPC Error: {res_json['error']}")
            return res_json.get("result")

    def get_block_number(self) -> int:
        """Returns the current block height on the Fantom network."""
        result = self._call_rpc("eth_blockNumber", [])
        return int(result, 16)

    def get_balance(self, address: str) -> float:
        """Returns the FTM balance of an address (in Wei converted to FTM)."""
        result = self._call_rpc("eth_getBalance", [address, "latest"])
        wei = int(result, 16)
        return wei / 1e18

    def estimate_gas(self, from_addr: str, to_addr: str, data: str = "0x") -> int:
        """Estimates gas needed for a transaction."""
        transaction = {
            "from": from_addr,
            "to": to_addr,
            "data": data
        }
        result = self._call_rpc("eth_estimateGas", [transaction])
        return int(result, 16)

    def get_gas_price(self) -> int:
        """Returns the current gas price in Wei."""
        result = self._call_rpc("eth_gasPrice", [])
        return int(result, 16)

    def call_contract(self, contract_address: str, data: str) -> str:
        """Calls a constant/pure contract function (read-only eth_call)."""
        transaction = {
            "to": contract_address,
            "data": data
        }
        return self._call_rpc("eth_call", [transaction, "latest"])

def main():
    print("Initializing Fantom RPC Client...")
    # Initialize pointing to the mainnet (or testnet if desired)
    client = FantomClient(FANTOM_MAINNET_RPC)

    try:
        # 1. Fetch current block number
        block = client.get_block_number()
        print(f"Current Fantom Block: {block}")

        # 2. Get balance of a test address
        test_address = "0x6B175474E89094C44Da98b954EedeAC495271d0F" # Sample address
        balance = client.get_balance(test_address)
        print(f"FTM Balance of {test_address}: {balance:.4f} FTM")

        # 3. Get current gas price
        gas_price = client.get_gas_price()
        print(f"Current Gas Price: {gas_price / 1e9:.2f} Gwei")

    except Exception as e:
        print(f"Error communicating with Fantom RPC: {e}", file=sys.stderr)

if __name__ == '__main__':
    main()
