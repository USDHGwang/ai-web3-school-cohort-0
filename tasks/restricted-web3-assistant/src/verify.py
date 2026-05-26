#!/usr/bin/env python3
"""
SafeTx Oracle — Phase 4: Post-Transaction Verification

Verifies a confirmed transaction by reading the receipt and parsing events.
AI can execute this. AI CANNOT sign or broadcast transactions.

Usage:
    python src/verify.py <transaction_hash>

Example:
    python src/verify.py 0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890
"""

import sys
import json
import urllib.request
import re

RPC_URL = "https://ethereum-rpc.publicnode.com"


def eth_get_transaction_receipt(tx_hash: str) -> dict | None:
    """Fetch a transaction receipt."""
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getTransactionReceipt",
        "params": [tx_hash],
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
    except Exception as e:
        print(f"Error: {e}")
        return None


def parse_transfer_events(logs: list) -> list:
    """Parse ERC-20 Transfer events from transaction logs.

    Transfer event signature: keccak256("Transfer(address,address,uint256)")
    = 0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef
    """
    transfer_sig = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
    transfers = []

    for log in logs:
        topics = log.get("topics", [])
        if len(topics) >= 3 and topics[0] == transfer_sig:
            transfers.append({
                "from": "0x" + topics[1][-40:],
                "to": "0x" + topics[2][-40:],
                "value": int(log.get("data", "0x0"), 16),
                "contract": log.get("address", ""),
            })

    return transfers


def wei_to_eth(wei: int) -> float:
    return wei / 1e18


def main():
    if len(sys.argv) < 2:
        print("Usage: python verify.py <transaction_hash>")
        sys.exit(1)

    tx_hash = sys.argv[1]
    if not re.match(r"^0x[a-fA-F0-9]{64}$", tx_hash):
        print(f"❌ Invalid transaction hash: {tx_hash}")
        sys.exit(1)

    tx_hash = tx_hash.lower()
    print(f"🔍 Verifying transaction: {tx_hash}")
    print()

    receipt = eth_get_transaction_receipt(tx_hash)
    if not receipt:
        print("❌ Could not fetch transaction receipt")
        print("   Check: Is the transaction confirmed?")
        print("   Check: Is the RPC node reachable?")
        sys.exit(1)

    # Parse receipt
    block = int(receipt.get("blockNumber", "0x0"), 16)
    status = int(receipt.get("status", "0x0"), 16)
    gas_used = int(receipt.get("gasUsed", "0x0"), 16)
    gas_price = int(receipt.get("effectiveGasPrice", "0x0"), 16)

    print(f"  Block:        {block}")
    print(f"  Status:       {'✅ Success' if status == 1 else '❌ Failed'}")
    print(f"  Gas used:     {gas_used:,}")
    print(f"  Gas price:    {gas_price / 1e9:.1f} gwei")
    print(f"  Tx cost:      {gas_used * gas_price / 1e18:.6f} ETH")
    print()

    # Parse Transfer events
    logs = receipt.get("logs", [])
    transfers = parse_transfer_events(logs)

    if transfers:
        print(f"📦 Transfer events ({len(transfers)}):")
        for t in transfers:
            addr_short = t["contract"][:10] + "..." + t["contract"][-6:]
            from_short = t["from"][:10] + "..." + t["from"][-6:]
            to_short = t["to"][:10] + "..." + t["to"][-6:]
            value_display = (
                f"{wei_to_eth(t['value']):.4f} ETH"
                if re.match(r"^0x0+$", t["contract"])
                else f"{t['value'] / 1e6:.2f} USDC"
                if t["contract"].lower() == "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
                else f"{t['value']:,} units"
            )
            print(f"    {from_short} → {to_short}")
            print(f"    Value: {value_display}")
            print(f"    Contract: {addr_short}")
            print()
    else:
        print("📦 No Transfer events found")
        print()

    # Summary
    print("=" * 50)
    print("VERIFICATION SUMMARY")
    print("=" * 50)
    if status == 1:
        print("✅ Transaction succeeded")
    else:
        print("❌ Transaction failed")
    print(f"  Tx cost: ${gas_used * gas_price / 1e18 * 3000:.2f}")
    if transfers:
        print(f"  Tokens transferred: {len(transfers)} events")
    print()
    print("⚠️  REMINDER: This is a post-hoc verification.")
    print("   The transaction has already been mined.")
    print("   AI did not and cannot sign this transaction.")
    print()


if __name__ == "__main__":
    main()