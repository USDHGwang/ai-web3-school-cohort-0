# SafeTx Oracle

> A restricted Web3 assistant design — AI helps plan, simulate, and verify blockchain transactions, but never touches private keys.

**Live demo workflow diagram**: [docs/workflow.md](docs/workflow.md)

---

## What Problem Does This Solve?

New DeFi users frequently lose funds because they:

- Approved **unlimited token allowances**
- Didn't notice a contract had **upgrade / pause / blacklist** functions
- Interacted with a **phishing site** pointing to a fake contract address
- Didn't check **slippage and gas costs** before signing
- Trusted a project's whitepaper without **verifying on-chain state**

**SafeTx Oracle** closes this gap: AI does the research and pre-flight checks; the user keeps custody and makes the final call.

---

## Core Principle

```
AI can:  Plan, research, simulate, generate warnings, verify results
AI cannot: Hold keys, sign transactions, broadcast txs, expose mnemonics
```

---

## Workflow

### Phase 1: Contract Security Scan (AI, Automated)

The AI independently checks the target contract:

| Check | Tool | What It Detects |
|-------|------|-----------------|
| Sourcify verification | `Sourcify API` | Full match vs partial match vs unverified |
| Creation bytecode match | `Sourcify metadata` | Constructor args differ from published source |
| Proxy detection | `Bytecode scan` | `delegatecall`, `upgradeTo()`, implementation slot |
| Dangerous functions | `4byte.directory` | `selfdestruct`, `mint`, `blacklist`, `pause` |
| Deployer forensics | `Etherscan / RPC` | Deployer history, fund source, past rug tokens |

**Output**: Security Report with ✅ / ⚠️ / ❌ verdicts per check.

### Phase 2: Transaction Simulation (AI-Assisted)

Before the user signs anything, the AI simulates the transaction:

1. **`eth_call` simulation** — dry-run the swap to see expected output
2. **Gas estimation** — cost in ETH and USD at current gas prices
3. **Slippage calculation** — min / expected / max output with confidence
4. **Token tax detection** — check if transfer fees apply
5. **Structured tx description** — plain-English summary of what the tx does

**Output**: Transaction Preview with estimated values and warnings.

### Phase 3: 🔴 Human Confirmation

The user takes over:

1. **Read the Security Report** and decide whether to proceed
2. **Enter transaction parameters** into wallet (MetaMask / Rabby / WalletConnect)
3. **Set token approval amount** — only the amount needed, never unlimited
4. **Visually verify** the contract address (first 6 + last 4 chars)
5. **Sign the transaction** in their wallet

> **AI never:** has access to the user's private key, seed phrase, or wallet extension.

### Phase 4: Post-Tx Verification (AI, Automated)

After the transaction is mined:

1. Read the **transaction receipt** via RPC
2. Parse **Transfer events** to find actual tokens received
3. Compare **expected output vs actual output**
4. Check if **slippage tolerance was honored**
5. Check the **authorized allowance** (was it returned? Reset to 0?)

**Output**: Result Summary with pass/fail verdict per check.

---

## Input & Output Examples

### Input

```
User: I want to swap 1.5 ETH for USDC on Ethereum mainnet.
Contract address: 0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640
My wallet: 0xAb58...F91C
I have 3 ETH total.
```

### Output: Security Report

```
## Security Report — 0x88e6...5640

✅ Sourcify: Full match (creation + runtime bytecode verified)
✅ Proxy: No proxy detected
⚠️ Function: transferOwnership() present (owner can change)
✅ No selfdestruct, no mint, no blacklist
✅ Deployer: 0x1F98...B3cD (funded from Binance, 3 contracts deployed,
   all standard Uniswap V3 pools — no rug history)

Verdict: SAFE — proceed with normal caution
```

### Output: Transaction Preview

```
## Transaction Preview

Action: Swap 1.5 ETH → USDC
Pool: Uniswap V3 (0.05% fee tier)
Expected output: 5,118.75 USDC
Slippage (0.5%): Min 5,093.16 USDC
Gas estimate: 0.009 ETH (~$27 @ 22 gwei)
Token tax: 0% (standard ERC-20)
Wallet after: 1.491 ETH remaining

⚠️ Recommended: Set approval to exactly 1.5 ETH,
   not "unlimited"
```

### Output: Result Summary

```
## Transaction Result

✅ Confirmed in block 21,045,892
Gas used: 189,432 (est. 210,000 — under estimate)
Actual received: 5,112.40 USDC
Expected: 5,118.75 USDC
Difference: -0.12% (within 0.5% slippage ✅)
Approval reset to 0 after swap? ✅ Yes
```

---

## Confirmation Points (🔴 Human Only)

| # | Step | 🔴 Human Action | AI Role |
|---|------|-----------------|---------|
| 1 | Contract review | Read & decide to proceed | Generate report |
| 2 | Tx parameters | Enter amount/slippage/gas in wallet | Suggest safe defaults |
| 3 | Token approval | Confirm approval tx in wallet | Recommend minimal amount |
| 4 | Address verification | Visually match contract address | Verify checksum |
| 5 | Signing | Sign with wallet | Describe what the tx does |
| 6 | Result check | Review comparison | Generate comparison |

---

## Risks & Limitations

### 1. Simulation ≠ Execution (`eth_call` vs `eth_sendRawTransaction`)

`eth_call` simulates a transaction against the current chain state. Between simulation and execution, the state can change — MEV bots, sandwich attacks, or other transactions can alter the actual outcome. **Users must set a reasonable slippage tolerance.** The AI's simulation is a best-effort estimate, not a guarantee.

### 2. Verified ≠ Safe

A Sourcify full match means the deployed bytecode matches the open-source code — it does NOT mean the code is secure. The contract may still contain:
- Logic bugs that only trigger under specific conditions
- Hidden admin functions that aren't in the public ABI
- Economic vulnerabilities (oracle manipulation, rounding errors)

**Verification proves authenticity, not safety.**

### 3. RPC Node Trust

The AI depends on public RPC nodes (e.g., publicnode.com) for all on-chain queries. These nodes could:
- Return stale / cached state
- Censor certain queries
- Be compromized and return false data

**The user's wallet connects to its own node / provider. If there's a discrepancy, the wallet's chain state is authoritative.**

### 4. RPC Provider Dependency (Availability)

If the AI's RPC provider is down or rate-limited, the entire pre-flight pipeline stalls. The user cannot get a Security Report or Transaction Preview until the RPC recovers. **The workflow has no fallback provider configuration** — this is a single-point-of-failure.

### 5. AI Hallucination

The AI may misinterpret bytecode patterns, misclassify function selectors, or draw incorrect conclusions about contract behavior. For example:
- A function selector `0x12345678` may match a dangerous function in one context but a benign one in another
- Bytecode analysis via regex is heuristic — it can miss obfuscated functions
- The AI's natural language summary of what a transaction does is an educated guess

**All AI-generated conclusions should be cross-referenced against the user's own understanding or a block explorer.**

---

## Requirements & Installation

```bash
# Clone the repo
git clone https://github.com/USDHGwang/restricted-web3-assistant.git
cd restricted-web3-assistant

# Install dependencies
pip install requests web3

# No API keys needed for read-only queries
# (Public RPC + Sourcify are free, no registration)
```

---

## How to Run

```bash
# Phase 1: Scan a contract
python src/scan.py 0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640

# Phase 2: Simulate a swap
python src/simulate.py \
  --contract 0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640 \
  --from 0xAb58...F91C \
  --amount 1.5 \
  --token-in ETH \
  --token-out USDC

# Phase 4: Verify a transaction
python src/verify.py 0xabcdef...12345678
```

---

## Project Structure

```
restricted-web3-assistant/
├── README.md               # This file
├── LICENSE
├── docs/
│   └── workflow.md         # Workflow diagram (Mermaid + ASCII)
├── src/
│   ├── scan.py             # Phase 1: Contract security scan
│   ├── simulate.py         # Phase 2: Transaction simulation
│   └── verify.py           # Phase 4: Post-tx verification
└── .gitignore
```

---

## Tech Stack

| Component | Tool | Purpose |
|-----------|------|---------|
| RPC Client | `web3.py` / `curl` | On-chain state queries |
| Contract Verification | `Sourcify API` | Bytecode verification |
| Function Signatures | `4byte.directory` | Function selector lookup |
| Deployer Forensics | `Etherscan` / RPC | Wallet history |
| Transaction Simulation | `eth_call` | Dry-run txs |
| Workflow Diagram | `Mermaid` | Visual pipeline |

---

## License

MIT

---

## Related

- [AIP Protocol](https://github.com/USDHGwang/aip-protocol) — On-chain agent security framework
- [DeFi Contract Forensics](https://github.com/USDHGwang/defi-contract-forensics) — Rug-check methodology