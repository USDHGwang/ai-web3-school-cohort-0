# SafeTx Oracle — Workflow

## Overview

```
User Input: "I want to swap 1 ETH for USDC on Uniswap V3, contract 0x88e6..."
         │
         ▼
┌─────────────────────────────────────────────────────┐
│  Phase 1: Contract Security Scan (AI, Automated)     │
│  ├── Sourcify verification check                     │
│  ├── Proxy / upgrade risk detection                  │
│  ├── Dangerous function signature scan               │
│  ├── Deployer wallet forensics                       │
│  └── Output: Security Report                         │
└─────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│  Phase 2: Transaction Simulation (AI-Assisted)      │
│  ├── Simulate swap via eth_call                      │
│  ├── Estimate gas cost & slippage                    │
│  ├── Check token transfer tax / fee                  │
│  ├── Generate structured transaction description     │
│  └── Output: Transaction Preview                     │
└─────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│  Phase 3: 🔴 Human Confirmation                     │
│  ├── 🔴 User reviews Security Report                 │
│  ├── 🔴 User checks transaction params in wallet     │
│  ├── 🔴 User sets approval amount (minimal)          │
│  ├── 🔴 User signs transaction in wallet             │
│  └── Output: Signed transaction broadcast to chain   │
└─────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│  Phase 4: Post-Tx Verification (AI, Automated)      │
│  ├── Read transaction receipt                        │
│  ├── Verify actual tokens received                   │
│  ├── Compare expected vs actual outcome              │
│  └── Output: Result Summary                          │
└─────────────────────────────────────────────────────┘
```

## Mermaid Diagram

```mermaid
graph TB
    subgraph User["User"]
        UInput["Input: Transaction Intent<br/>(contract, amount, action)"]
    end

    subgraph Phase1["Phase 1: Contract Security Scan (AI)"]
        Sourcify["Sourcify Verification"]
        Proxy["Proxy / Upgrade Detection"]
        FuncScan["Dangerous Function Scan"]
        Deployer["Deployer Forensics"]
        Report["Security Report"]
        Sourcify --> Proxy --> FuncScan --> Deployer --> Report
    end

    subgraph Phase2["Phase 2: Transaction Simulation (AI-Assisted)"]
        Sim["eth_call Simulation"]
        Gas["Gas & Slippage Estimate"]
        Tax["Token Tax Check"]
        Preview["Transaction Preview"]
        Sim --> Gas --> Tax --> Preview
    end

    subgraph Phase3["Phase 3: 🔴 Human Confirmation"]
        H1["🔴 Review Security Report"]
        H2["🔴 Check params in wallet"]
        H3["🔴 Set approval (minimal)"]
        H4["🔴 Sign in wallet"]
        Signed["Signed Transaction"]
        H1 --> H2 --> H3 --> H4 --> Signed
    end

    subgraph Phase4["Phase 4: Post-Tx Verification (AI)"]
        Receipt["Read Transaction Receipt"]
        Verify["Verify Tokens Received"]
        Compare["Compare Expected vs Actual"]
        Summary["Result Summary"]
        Receipt --> Verify --> Compare --> Summary
    end

    UInput --> Phase1
    Report --> Phase2
    Preview --> Phase3
    Signed -.->|"Broadcast via User's Wallet"| Blockchain[("Ethereum")]
    Blockchain -.->|"Confirm Tx"| Phase4
    Summary --> User

    %% Annotations
    classDef ai fill:#e3f2fd,stroke:#1565c0
    classDef human fill:#fff3e0,stroke:#e65100
    classDef blockchain fill:#f3e5f5,stroke:#7b1fa2

    class Sourcify,Proxy,FuncScan,Deployer,Report,Sim,Gas,Tax,Preview,Receipt,Verify,Compare,Summary ai
    class H1,H2,H3,H4,Signed human
    class Blockchain blockchain
```

## Color Legend

| Color | Role |
|-------|------|
| 🔵 Blue | AI automated step |
| 🟠 Orange | 🔴 Human confirmation required |
| 🟣 Purple | Blockchain / network layer |

## Confirmation Points

| Step | AI Does | 🔴 Human Does |
|------|---------|---------------|
| Contract scan | Execute & interpret | Read report, decide to proceed |
| Transaction params | Suggest values | Enter into wallet |
| Token approval | Check requirement, suggest minimal | Confirm approval tx |
| Signing | Generate EIP-712 description | Sign in wallet |
| Address check | Verify checksum | Visually verify full address |
| Result check | Read receipt, compare | Review comparison |