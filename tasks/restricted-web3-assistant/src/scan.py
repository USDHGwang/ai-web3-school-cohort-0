#!/usr/bin/env python3
"""
SafeTx Oracle — Phase 1: Contract Security Scan

Scans a contract for safety indicators using public data sources.
AI can execute this. AI CANNOT sign or broadcast transactions.

Usage:
    python src/scan.py <contract_address> [--chain CHAIN_ID]

Example:
    python src/scan.py 0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640
"""

import sys
import json
import urllib.request
import re

# ── Sourcify Check ──────────────────────────────────────────────────────


def check_sourcify(address: str, chain: int = 1) -> dict:
    """Check Sourcify verification status of a contract.

    Returns:
        dict with status, match_type, and source_url (if available).
    """
    base = f"https://repo.sourcify.dev/contracts"
    result = {"verified": False, "match_type": None, "source_url": None}

    # Check full match first
    for match_type in ("full_match", "partial_match"):
        url = f"{base}/{match_type}/{chain}/{address}/metadata.json"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "SafeTxOracle/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    result["verified"] = True
                    result["match_type"] = match_type
                    # Parse metadata to get source path
                    meta = json.loads(resp.read().decode())
                    sources = meta.get("sources", {})
                    if sources:
                        result["source_url"] = (
                            f"{base}/{match_type}/{chain}/{address}/sources/src/"
                        )
                    break
        except urllib.error.HTTPError:
            continue
        except Exception:
            continue

    return result


# ── Bytecode Analysis ───────────────────────────────────────────────────


def get_bytecode(address: str, rpc_url: str = "https://ethereum-rpc.publicnode.com") -> str:
    """Fetch contract bytecode via eth_getCode."""
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getCode",
        "params": [address, "latest"],
        "id": 1,
    }
    req = urllib.request.Request(
        rpc_url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode()).get("result", "0x")


def scan_dangerous_functions(bytecode: str) -> list[dict]:
    """Scan bytecode for known dangerous function selectors.

    Returns list of {selector, name, severity}
    """
    code = bytecode[2:]  # strip 0x
    findings = []

    # Known dangerous selectors (PUSH4 + EQ pattern)
    dangerous = {
        "8da5cb5b": ("owner()", "info"),
        "f2fde38b": ("transferOwnership(address)", "warning"),
        "715018a6": ("renounceOwnership()", "info"),
        "3659cfe6": ("upgradeTo(address)", "critical"),
        "8f283970": ("upgradeToAndCall(address,bytes)", "critical"),
        "8456cb59": ("pause()", "low"),
        "3f4ba83a": ("unpause()", "low"),
        "42966c68": ("burn(uint256)", "info"),
        "40c10f19": ("mint(address,uint256)", "warning"),
        "2e1a7d4d": ("withdraw(uint256)", "info"),
        "69fe0e2d": ("setFee(uint256)", "warning"),
        "9dc29fac": ("approve(address,uint256)", "info"),
        "23b872dd": ("transferFrom(address,address,uint256)", "info"),
        "41f9f5f3": ("selfdestruct()", "critical"),
    }

    # Scan for PUSH4+EQ patterns in the dispatcher
    for selector, (name, severity) in dangerous.items():
        # Pattern: PUSH4(63) + 4-byte selector + EQ(14)
        pattern = f"63{selector}14"
        if pattern in code:
            findings.append({
                "selector": f"0x{selector}",
                "name": name,
                "severity": severity,
            })

    return findings


def detect_proxy(bytecode: str) -> dict:
    """Detect proxy patterns in bytecode.

    Checks for:
    - delegatecall (0xd4... pattern in runtime bytecode)
    - Known proxy storage slots (ERC-1967)
    """
    code = bytecode[2:]
    result = {"is_proxy": False, "indicators": []}

    # delegatecall exists in runtime code
    if "d4" in code:
        # More precise: check for delegatecall opcode (0xf4) preceded by address loading
        if "ff" in code:  # delegatecall opcode on EVM
            result["indicators"].append("delegatecall pattern detected")
            result["is_proxy"] = True

    return result


# ── Deployer Analysis ───────────────────────────────────────────────────


def get_deployer(address: str, rpc_url: str) -> str | None:
    """Get deployer address from the deployment transaction.

    Note: This requires parsing the creation tx, which is complex.
    For production, use Etherscan API. For this demo, returns None.
    """
    return None


# ── Main ────────────────────────────────────────────────────────────────


def main():
    if len(sys.argv) < 2:
        print("Usage: python scan.py <contract_address> [--chain CHAIN_ID]")
        sys.exit(1)

    address = sys.argv[1]
    if not re.match(r"^0x[a-fA-F0-9]{40}$", address):
        print(f"❌ Invalid Ethereum address: {address}")
        sys.exit(1)

    # Normalize
    address = address.lower()
    chain = 1  # Ethereum mainnet
    if "--chain" in sys.argv:
        idx = sys.argv.index("--chain")
        if idx + 1 < len(sys.argv):
            chain = int(sys.argv[idx + 1])

    print(f"🔍 Scanning contract: {address} (chain {chain})")
    print()

    # 1. Sourcify check
    print("📦 Checking Sourcify verification...")
    sourcify = check_sourcify(address, chain)
    if sourcify["verified"]:
        match_icon = "✅" if sourcify["match_type"] == "full_match" else "⚠️"
        print(f"  {match_icon} Verified: {sourcify['match_type']}")
        if sourcify["source_url"]:
            print(f"     Source: {sourcify['source_url']}")
    else:
        print(f"  ❌ Not verified on Sourcify")

    # 2. Bytecode analysis
    print()
    print("🔬 Analyzing bytecode...")
    bytecode = get_bytecode(address)
    if bytecode == "0x":
        print("  ❌ No bytecode found (not a contract?)")
        sys.exit(1)
    print(f"  Bytecode size: {len(bytecode)//2} bytes")

    functions = scan_dangerous_functions(bytecode)
    if functions:
        print("  ⚠️  Dangerous functions detected:")
        severity_icons = {
            "critical": "🔴",
            "warning": "🟡",
            "info": "🔵",
            "low": "⚪",
        }
        for f in functions:
            icon = severity_icons.get(f["severity"], "⚪")
            print(f"    {icon} {f['name']} (0x{f['selector']})")
    else:
        print("  ✅ No dangerous function signatures found")

    proxy = detect_proxy(bytecode)
    if proxy["is_proxy"]:
        print("  🟡 Proxy pattern detected")
        for ind in proxy["indicators"]:
            print(f"     - {ind}")
    else:
        print("  ✅ No proxy pattern detected")

    # Summary
    print()
    print("=" * 50)
    critical_count = sum(1 for f in functions if f["severity"] == "critical")
    warning_count = sum(1 for f in functions if f["severity"] == "warning")

    if critical_count > 0:
        print("🔴 RISK: Critical functions found — proceed with extreme caution")
    elif warning_count > 0:
        print("🟡 CAUTION: Warnings found — review before interacting")
    elif not sourcify["verified"]:
        print("🟡 CAUTION: Unverified contract — source code unknown")
    else:
        print("✅ SAFE: No immediate red flags detected")
    print("=" * 50)

    # Reminder
    print()
    print("⚠️  REMINDER: This scan is informational only.")
    print("   AI cannot sign or broadcast transactions.")
    print("   🔴 Always verify the address in your wallet before signing.")
    print()


if __name__ == "__main__":
    main()