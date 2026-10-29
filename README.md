---
license: mit
tags:
- heart-sound
- murmur
- audio
- onnx
- streamlit
- rust
---

# Heart Murmer Agentic Hive

A multi-agent heart sound (murmur) detector with federated learning, P2P exchange, and security hardening.

## Features
- **Multi-agent pipeline:** preprocessing, inference, decision, safety, visualization.
- **ONNX Runtime** (CPU) with AST model (~83 MB).
- **Linear probe** for murmur detection.
- **P2P exchange:** signed bundles, promotion gate, rollback.
- **Security:** Ed25519 identity, hash verification, rate limiting, resource guard, durable queue, NTFS ACL, audit log hash chain.
- **LAN discovery:** UDP broadcast peer discovery.
- **Rust port:** one-click installer (no dependencies).
- **Human-in-the-loop:** correction feedback.

## How to use
### Python (Streamlit)
1. Install Python 3.10+.
2. Run `setup.bat` (creates venv, installs deps, downloads model).
3. Run `run.bat` → opens http://localhost:8501.
4. Upload a heart-sound audio file → click Analyze.

### Rust (one-click)
1. Download `heart-murmer-agentic-hive-setup.exe`.
2. Run installer → launch from Start Menu.

## License
Dual license: MIT for base components; copyright © 2026 Ahsan Mandhar for applied technology. See LICENSE.md.

## Citation
If you use this work in research or presentation, please credit: Ahsan Mandhar.
## Download

### Python (one-click installer — recommended for lay users)
[![Download Python Installer](https://img.shields.io/badge/Download-Python%20Installer-green?style=for-the-badge)](https://huggingface.co/Ahsanmandhar/heart-murmer-agentic-hive-works/resolve/main/heart-murmer-agentic-hive-python-setup.exe)

### Rust (one-click installer — CLI)
[![Download Rust Installer](https://img.shields.io/badge/Download-Rust%20Installer-blue?style=for-the-badge)](https://huggingface.co/Ahsanmandhar/heart-murmer-agentic-hive-works/resolve/main/heart-murmer-agentic-hive-setup.exe)

### Python (source)
[![Download Python ZIP](https://img.shields.io/badge/Download-Python%20Source-gray?style=for-the-badge)](https://github.com/ahsanmandhar-ui/heart-murmer-agentic-hive-works/archive/refs/heads/main.zip)

### Network Topology
```mermaid
%%{init: {'theme':'base','themeVariables':{'primaryTextColor':'#000000','lineColor':'#1f2937','fontSize':'15px'}}}%%
flowchart LR
    A["Node A<br/>(Python)"]:::py
    B["Node B<br/>(Rust)"]:::rs
    C["Node C<br/>(Python)"]:::py
    LAN(("LAN<br/>UDP broadcast<br/>and TCP")):::lan

    A <-->|"signed bundle"| B
    B <-->|"signed bundle"| C
    A <-->|"signed bundle"| C
    A -.- LAN
    B -.- LAN
    C -.- LAN

    classDef py fill:#f59e0b,stroke:#b45309,stroke-width:3px,color:#000000
    classDef rs fill:#3b82f6,stroke:#1d4ed8,stroke-width:3px,color:#000000
    classDef lan fill:#8b5cf6,stroke:#6d28d9,stroke-width:3px,color:#000000
```

### Node Bootstrap & Discovery
```mermaid
%%{init: {'theme':'base','themeVariables':{'fontSize':'14px','lineColor':'#1f2937','primaryTextColor':'#000000'}}}%%
sequenceDiagram
    autonumber
    participant N as New Node
    participant K as Key Store<br/>(node.key / node.pub)
    participant L as LAN
    participant P as Peer List

    rect rgb(245, 158, 11)
    Note over N,K: BOOTSTRAP (first run)
    N->>K: generate Ed25519 keypair
    K-->>N: node.pub is node identity
    end

    rect rgb(59, 130, 246)
    Note over N,L: DISCOVERY (network.py)
    N->>L: UDP broadcast on known port
    L-->>N: IP, port, and signed heartbeat
    end

    rect rgb(16, 185, 129)
    Note over N,P: RESULT
    N->>P: populate live peer list
    P-->>N: peers displayed in sidebar
    end
```
### Bundle Exchange Protocol
```mermaid
%%{init: {'theme':'base','themeVariables':{'fontSize':'14px','lineColor':'#1f2937','primaryTextColor':'#000000'}}}%%
sequenceDiagram
    autonumber
    participant A as Node A (export)
    participant B as Node B (import)
    participant Log as exchange_log.jsonl

    rect rgb(236, 72, 153)
    Note over A: EXPORT
    A->>A: collect probe.json, manifest.json, feedback corrections
    A->>A: compute SHA-256 for each file
    A->>A: sign manifest with Ed25519
    A->>A: create exchange_bundle.zip
    end

    rect rgb(59, 130, 246)
    Note over A,B: TRANSPORT (exchange.py)
    A->>B: send 8-byte size header and zip data over TCP
    B-->>A: ACK response
    end

    rect rgb(16, 185, 129)
    Note over B,Log: IMPORT
    B->>B: save zip to temp
    B->>B: verify required files are present
    B->>B: check probe_hash matches SHA-256 of probe.json
    B->>B: extract probe_imported.json and manifest_imported.json
    B->>Log: append hash-chained event
    end
```

### Promotion Gate
```mermaid
%%{init: {'theme':'base','themeVariables':{'fontSize':'14px','lineColor':'#1f2937','primaryTextColor':'#000000'}}}%%
flowchart TD
    S(["Peer bundle received"]):::start
    H{"Hash integrity:<br/>SHA-256 match?"}:::chk
    M{"Metric comparison:<br/>Peer AUC exceeds local<br/>by threshold?"}:::chk
    AB{"Abstention safety:<br/>Peer rate not higher?"}:::chk
    RG{"Resource guard:<br/>RAM, disk, CPU acceptable?"}:::chk
    P["PROMOTE<br/>swap probe.json"]:::ok
    BK["Backup previous probe"]:::ok
    R["REJECT<br/>keep local probe"]:::bad
    RB["ROLLBACK<br/>restore backup"]:::warn

    S --> H
    H -- "pass" --> M
    H -- "fail" --> R
    M -- "pass" --> AB
    M -- "fail" --> R
    AB -- "pass" --> RG
    AB -- "fail" --> R
    RG -- "pass" --> P
    RG -- "fail" --> R
    P --> BK
    BK -. "promotion failure" .-> RB

    classDef start fill:#3b82f6,stroke:#1d4ed8,stroke-width:3px,color:#000000
    classDef chk fill:#f59e0b,stroke:#b45309,stroke-width:3px,color:#000000
    classDef ok fill:#10b981,stroke:#047857,stroke-width:3px,color:#000000
    classDef bad fill:#ef4444,stroke:#b91c1c,stroke-width:3px,color:#000000
    classDef warn fill:#f97316,stroke:#c2410c,stroke-width:3px,color:#000000
```
### Training Flow (No Raw Audio Sharing)
```mermaid
%%{init: {'theme':'base','themeVariables':{'fontSize':'14px','lineColor':'#1f2937','primaryTextColor':'#000000'}}}%%
flowchart LR
    U["User corrects<br/>a prediction"]:::user
    F["feedback.jsonl<br/>with embeddings"]:::data
    T["retrain_probe.py<br/>periodic or offline"]:::train
    PR["probe.json<br/>AUC improves"]:::model
    EX["export bundle<br/>signed and hashed"]:::net
    PEER["Peer imports<br/>and applies gate"]:::net

    U --> F --> T --> PR --> EX --> PEER
    PEER -. "no raw audio shared" .-> F

    classDef user fill:#f59e0b,stroke:#b45309,stroke-width:3px,color:#000000
    classDef data fill:#8b5cf6,stroke:#6d28d9,stroke-width:3px,color:#000000
    classDef train fill:#06b6d4,stroke:#0e7490,stroke-width:3px,color:#000000
    classDef model fill:#10b981,stroke:#047857,stroke-width:3px,color:#000000
    classDef net fill:#ec4899,stroke:#be185d,stroke-width:3px,color:#000000
```

### Risk Mitigation
```mermaid
%%{init: {'theme':'base','themeVariables':{'fontSize':'13px','lineColor':'#1f2937','primaryTextColor':'#000000'}}}%%
flowchart LR
    subgraph RISKS["Risks"]
        direction TB
        R1["Model drift"]:::risk
        R2["Feedback poisoning"]:::risk
        R3["Overfitting to<br/>few corrections"]:::risk
        R4["Runaway adoption"]:::risk
        R5["Stale models"]:::risk
        R6["Tampering"]:::risk
    end

    subgraph FIXES["Mitigations"]
        direction TB
        F1["Improvement threshold<br/>in promotion gate"]:::fix
        F2["Signed corrections,<br/>hash chain, rate limiting"]:::fix
        F3["Retrain only when<br/>enough new samples exist"]:::fix
        F4["Resource guard<br/>pauses exchange"]:::fix
        F5["hive_queue.py<br/>SQLite, backoff, recover()"]:::fix
        F6["NTFS ACLs and<br/>Ed25519 manifests"]:::fix
    end

    R1 --> F1
    R2 --> F2
    R3 --> F3
    R4 --> F4
    R5 --> F5
    R6 --> F6

    classDef risk fill:#ef4444,stroke:#b91c1c,stroke-width:3px,color:#000000
    classDef fix fill:#3b82f6,stroke:#1d4ed8,stroke-width:3px,color:#000000
```

### End-to-End Propagation
```mermaid
%%{init: {'theme':'base','themeVariables':{'fontSize':'14px','lineColor':'#1f2937','primaryTextColor':'#000000'}}}%%
sequenceDiagram
    autonumber
    participant A as Node A
    participant B as Node B
    participant C as Node C

    rect rgb(245, 158, 11)
    Note over A: 50 corrected samples received
    A->>A: retrain probe
    Note over A: AUC improves from 0.8796 to 0.8920
    end

    rect rgb(59, 130, 246)
    Note over A,B: EXCHANGE
    A->>B: export bundle and send
    B->>B: verify hash
    B->>B: gate passes because 0.8920 exceeds 0.8796 by threshold
    Note over B: PROMOTE
    end

    rect rgb(16, 185, 129)
    Note over B,C: PROPAGATION
    C->>B: discover peer
    B->>C: send bundle
    C->>C: gate and promote if better
    end

    Note over A,C: Knowledge spreads without central training or raw audio sharing
```
