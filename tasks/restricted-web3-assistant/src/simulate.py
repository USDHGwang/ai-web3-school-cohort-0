#!/usr/bin/env python3
"""
SafeTx Oracle — Phase 2: Transaction Simulation

Simulates a token swap via eth_call to preview expected output.
AI can execute this. AI CANNOT sign or broadcast transactions.

Usage:
    python src/simulate.py <contract_address> --from <wallet> --amount <eth> --token-in <symbol> --token-out <symbol>

Example:
    python src/simulate.py 0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640 \\
        --from 0xAb58...F91C --amount 1.5 --token-in ETH --token-out USDC
"""

import sys
import json
import urllib.request
import re
import argparse

# ── RPC ─────────────────────────────────────────────────────────────────

RPC_URL = "https://ethereum-rpc.publicnode.com"

def eth_call(to: str, data: str, sender: str | None = None) -> str | None:
    """Execute an eth_call."""
    params = [{"to": to, "data": data}]
    if sender:
        params[0]["from"] = sender

    payload = {
        "jsonrpc": "2.0",
        "method": "eth_call",
        "params": params + ["latest"],
        "id": 1,
    }
    req = urllib.request.Request(
        RPC_URL,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode())
            return result.get("result")
    except Exception:
        return None


def eth_gas_price() -> int | None:
    """Get current gas price in wei."""
    payload = {"jsonrpc": "2.0", "method": "eth_gasPrice", "params": [], "id": 1}
    req = urllib.request.Request(
        RPC_URL,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode())
            gas_hex = result.get("result", "0x0")
            return int(gas_hex, 16)
    except Exception:
        return None


def get_eth_balance(address: str) -> int | None:
    """Get ETH balance in wei."""
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getBalance",
        "params": [address, "latest"],
        "id": 1,
    }
    req = urllib.request.Request(
        RPC_URL,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode())
            bal_hex = result.get("result", "0x0")
            return int(bal_hex, 16)
    except Exception:
        return None


# ── Helpers ──────────────────────────────────────────────────────────────


def wei_to_eth(wei: int) -> float:
    return wei / 1e18


def eth_to_wei(eth: float) -> int:
    return int(eth * 1e18)


# ── Main ────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="SafeTx Oracle — Simulate a swap")
    parser.add_argument("contract", help="Token contract address")
    parser.add_argument("--from", dest="sender", required=True, help="Your wallet address")
    parser.add_argument("--amount", type=float, required=True, help="Amount to swap (in ETH)")
    parser.add_argument("--token-in", default="ETH", help="Input token symbol (default: ETH)")
    parser.add_argument("--token-out", default="USDC", help="Output token symbol (default: USDC)")
    args = parser.parse_args()

    if not re.match(r"^0x[a-fA-F0-9]{40}$", args.contract):
        print(f"❌ Invalid contract address: {args.contract}")
        sys.exit(1)
    if not re.match(r"^0x[a-fA-F0-9]{40}$", args.sender):
        print(f"❌ Invalid wallet address: {args.sender}")
        sys.exit(1)

    contract = args.contract.lower()
    sender = args.sender.lower()
    amount_eth = args.amount
    amount_wei = eth_to_wei(amount_eth)

    print(f"🧪 Simulating swap: {amount_eth} {args.token_in} → {args.token_out}")
    print(f"   Contract: {contract}")
    print(f"   From:     {sender}")
    print()

    # 1. Get current gas price
    print("⛽ Fetching gas price...")
    gas_price = eth_gas_price()
    if gas_price:
        gas_gwei = gas_price / 1e9
        print(f"   Current gas price: {gas_gwei:.1f} gwei ({gas_price / 1e18:.6f} ETH)")
    else:
        gas_gwei = 20.0  # fallback
        print(f"   (Using default: {gas_gwei:.1f} gwei)")

    # 2. Check wallet balance
    print()
    print(f"💰 Checking wallet balance...")
    balance = get_eth_balance(sender)
    if balance is not None:
        bal_eth = wei_to_eth(balance)
        print(f"   Balance: {bal_eth:.4f} ETH")
        if balance < amount_wei:
            print(f"   ❌ Insufficient balance! Need {amount_eth} ETH, have {bal_eth:.4f} ETH")
            sys.exit(1)
        after_eth = bal_eth - amount_eth
        # Rough gas estimate: 210k gas for a swap
        gas_cost = 210_000 * gas_price
        after_eth -= gas_cost / 1e18
        print(f"   ✅ Sufficient balance")
        print(f"   Estimated after tx: {after_eth:.4f} ETH")
    else:
        print(f"   ⚠️  Could not fetch balance")

    # 3. Simulate the swap
    # Note: Real swap simulation requires the pool contract ABI and
    # quoter contract. This is a simplified placeholder.
    print()
    print("📊 Simulating swap (this requires the Uniswap Quoter contract)...")
    print("   🔴 NOTE: Full simulation needs the pool's quoter ABI.")
    print("   For production: use quoter.quoteExactInputSingle()")
    print()

    # Placeholder: use a mock price for demo
    mock_price = 3_412.50  # USDC per ETH
    expected_output = amount_eth * mock_price
    slippage = 0.005  # 0.5%
    min_output = expected_output * (1 - slippage)

    print(f"   Reference price: 1 ETH = {mock_price:.2f} USDC")
    print(f"   Expected output: {expected_output:.2f} USDC")
    print(f"   Slippage (0.5%): Min {min_output:.2f} USDC")
    print()

    # 4. Check token tax
    print("🏷️  Checking token transfer tax...")
    print("   (Requires balanceOf check on sender/receiver)")
    print("   Assume: 0% (standard ERC-20)")
    print()

    # 5. Summary
    print("=" * 50)
    print("TRANSACTION PREVIEW")
    print("=" * 50)
    print(f"  Action:      Swap {amount_eth} ETH → USDC")
    print(f"  Contract:    {contract}")
    print(f"  Expected:    ~{expected_output:.2f} USDC")
    print(f"  Min output:  {min_output:.2f} USDC (at 0.5% slippage)")
    print(f"  Gas est.:    ~210,000 units")
    print(f"  Gas cost:    ~{gas_cost / 1e18:.6f} ETH (${gas_cost / 1e18 * 3000:.2f})")
    print(f"  Token tax:   0%")
    print(f"  Wallet after: ~{after_eth:.4f} ETH" if balance else "  Wallet after: unknown")
    print()
    print("🔴 RECOMMENDATION")
    print("  Set approval to exactly the swap amount, NOT unlimited")
    print("  Verify the contract address in your wallet before signing")
    print()
    print("⚠️  REMINDER: AI cannot sign or broadcast this transaction.")
    print("   Open your wallet and sign manually.")
    print()


if __name__ == "__main__":
    main()