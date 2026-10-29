# Master Metrics - Heart Murmur Agentic Hive

![Master Metrics](docs/assets/master_metrics.png)

# Part 1: Model Artifact / Original AST / Circor Scaling

```mermaid
flowchart TB
    classDef domain fill:#FF00FF,stroke:#000000,stroke-width:3px,color:#000000,font-weight:bold
    classDef implemented fill:#00FF00,stroke:#000000,stroke-width:2px,color:#000000,font-weight:bold
    classDef reported fill:#00FFFF,stroke:#000000,stroke-width:2px,color:#000000,font-weight:bold

    ROOT["Part 1: Model Artifact / Original AST / Circor Scaling"]:::domain

    subgraph MA["Model Artifact"]
        MA1["Model file: Eheart_sound_by_Ahsan_Mandhar.onnx<br/>Source: Context summary<br/>Status: Implemented"]:::implemented
        MA2["Model type: AST, INT8 ONNX<br/>Source: Context summary<br/>Status: Implemented"]:::implemented
        MA3["Model size: 83 MB<br/>Source: Context summary<br/>Status: Implemented"]:::implemented
        MA4["Input shape: 1 x 1 x 80 x 1001<br/>Source: Context summary / PWA README<br/>Status: Implemented"]:::implemented
        MA5["Output shape: 1 x 311 x 768<br/>Source: Context summary / PWA README<br/>Status: Implemented"]:::implemented
        MA6["Pooled embedding: 768-dim<br/>Source: Context summary / PWA README<br/>Status: Implemented"]:::implemented
        MA7["Classifier: Linear probe probe.json<br/>Source: Context summary / PWA README<br/>Status: Implemented"]:::implemented
    end

    subgraph OA["Original AST"]
        OA1["Model size: 345 MB FP32<br/>Source: Context summary<br/>Status: Reported"]:::reported
        OA2["Load time: 1.59 s<br/>Source: Context summary<br/>Status: Reported"]:::reported
        OA3["p50 latency: 3.29 s<br/>Source: Context summary<br/>Status: Reported"]:::reported
        OA4["200-sample accuracy: 77.0%<br/>Source: Context summary<br/>Status: Reported"]:::reported
        OA5["AUC: 0.9262<br/>Source: Context summary<br/>Status: Reported"]:::reported
        OA6["Sensitivity: 0.560<br/>Source: Context summary<br/>Status: Reported"]:::reported
        OA7["Specificity: 0.980<br/>Source: Context summary<br/>Status: Reported"]:::reported
    end

    subgraph CS["Circor Scaling"]
        CS1["20 samples: 60% accuracy<br/>Source: Context summary<br/>Status: Reported"]:::reported
        CS2["50 samples: 74% accuracy<br/>Source: Context summary<br/>Status: Reported"]:::reported
        CS3["100 samples: 80% accuracy<br/>Source: Context summary<br/>Status: Reported"]:::reported
        CS4["200 samples: 81.5% accuracy excluding uncertain<br/>Source: Context summary<br/>Status: Reported"]:::reported
    end

    ROOT --> MA
    ROOT --> OA
    ROOT --> CS
    OA --> CS
```
```
# Part 2: Held-out Probe / Python App Eval

```mermaid
flowchart TB
    classDef domain fill:#FF00FF,stroke:#000000,stroke-width:3px,color:#000000,font-weight:bold
    classDef reported fill:#00FFFF,stroke:#000000,stroke-width:2px,color:#000000,font-weight:bold

    ROOT["Part 2: Held-out Probe / Python App Eval"]:::domain

    subgraph HP["Held-out Probe"]
        HP1["Accuracy before: 77.94%<br/>Source: Context summary<br/>Status: Reported"]:::reported
        HP2["Accuracy after: 80.88%<br/>Source: Context summary<br/>Status: Reported"]:::reported
        HP3["AUC before: 0.8478<br/>Source: Context summary<br/>Status: Reported"]:::reported
        HP4["AUC after: 0.8910<br/>Source: Context summary<br/>Status: Reported"]:::reported
        HP5["Samples: 69<br/>Source: Context summary<br/>Status: Reported"]:::reported
    end

    subgraph PY["Python App Eval"]
        PY1["TP: 39, FN: 10, FP: 8, TN: 41<br/>Source: PWA README<br/>Status: Reported"]:::reported
        PY2["Evaluated samples: 98, 2 uncertain<br/>Source: PWA README<br/>Status: Reported"]:::reported
        PY3["Accuracy: 0.8163<br/>Source: PWA README<br/>Status: Reported"]:::reported
        PY4["Sensitivity: 0.7959<br/>Source: PWA README<br/>Status: Reported"]:::reported
        PY5["Specificity: 0.8367<br/>Source: PWA README<br/>Status: Reported"]:::reported
        PY6["Precision: 0.8298, F1: 0.8125<br/>Source: PWA README<br/>Status: Reported"]:::reported
        PY7["AUC: 0.8796<br/>Source: PWA README<br/>Status: Reported"]:::reported
        PY8["Abstention rate: 2%<br/>Source: PWA README<br/>Status: Reported"]:::reported
        PY9["Inference p95: 144.64 ms<br/>Source: PWA README<br/>Status: Reported"]:::reported
    end

    ROOT --> HP
    ROOT --> PY
    HP --> PY
```
```
# Part 3: Rust Port / Rust vs Python

```mermaid
flowchart TB
    classDef domain fill:#FF00FF,stroke:#000000,stroke-width:3px,color:#000000,font-weight:bold
    classDef reported fill:#00FFFF,stroke:#000000,stroke-width:2px,color:#000000,font-weight:bold

    ROOT["Part 3: Rust Port / Rust vs Python"]:::domain

    subgraph RS["Rust Port"]
        RS1["Load time: ~200 ms<br/>Source: Context summary<br/>Status: Reported"]:::reported
        RS2["p50 latency: ~120 ms<br/>Source: Context summary<br/>Status: Reported"]:::reported
        RS3["End-to-end time: 3.245 s<br/>Source: Context summary<br/>Status: Reported"]:::reported
        RS4["Peak memory: 158.9 MB<br/>Source: Context summary<br/>Status: Reported"]:::reported
        RS5["Accuracy: 80.0%<br/>Source: Context summary<br/>Status: Reported"]:::reported
        RS6["AUC: 0.8888<br/>Source: Context summary<br/>Status: Reported"]:::reported
        RS7["Sensitivity: 0.690<br/>Source: Context summary<br/>Status: Reported"]:::reported
        RS8["Specificity: 0.910<br/>Source: Context summary<br/>Status: Reported"]:::reported
    end

    subgraph RV["Rust vs Python"]
        RV1["End-to-end speedup: ~2.25x<br/>Source: Context summary<br/>Status: Reported"]:::reported
        RV2["Memory reduction: 34% lower<br/>Source: Context summary<br/>Status: Reported"]:::reported
    end

    ROOT --> RS
    ROOT --> RV
    RS --> RV
```
```
# Part 4: Hive / Security

```mermaid
flowchart TB
    classDef domain fill:#FF00FF,stroke:#000000,stroke-width:3px,color:#000000,font-weight:bold
    classDef implemented fill:#00FF00,stroke:#000000,stroke-width:2px,color:#000000,font-weight:bold
    classDef reported fill:#00FFFF,stroke:#000000,stroke-width:2px,color:#000000,font-weight:bold
    classDef planned fill:#FFA500,stroke:#000000,stroke-width:2px,color:#000000,font-weight:bold

    ROOT["Part 4: Hive / Security"]:::domain

    subgraph HV["Hive"]
        HV1["Two-node integration test: all checks passed<br/>Source: Context summary<br/>Status: Reported in simulation"]:::reported
        HV2["Cross-device LAN/P2P test: not performed<br/>Source: Context summary<br/>Status: Planned / Not validated"]:::planned
    end

    subgraph SEC["Security"]
        SEC1["Ed25519 identity<br/>Status: Implemented"]:::implemented
        SEC2["Signed manifests<br/>Status: Implemented"]:::implemented
        SEC3["Bundle exchange<br/>Status: Implemented"]:::implemented
        SEC4["Promotion gate<br/>Status: Implemented"]:::implemented
        SEC5["LAN discovery<br/>Status: Implemented"]:::implemented
        SEC6["Resource guard<br/>Status: Implemented"]:::implemented
        SEC7["Durable queue<br/>Status: Implemented"]:::implemented
        SEC8["Secure storage<br/>Status: Implemented"]:::implemented
        SEC9["Hash-chained audit log<br/>Status: Implemented"]:::implemented
        SEC10["SHA-256 hashes<br/>Status: Implemented"]:::implemented
        SEC11["Rate limiting<br/>Status: Implemented"]:::implemented
        SEC12["NTFS ACLs<br/>Status: Implemented"]:::implemented
    end

    ROOT --> HV
    ROOT --> SEC
    HV1 --> HV2
    SEC --> HV
```
```
# Part 5: Comparison / Key Gaps / Status Legend

```mermaid
flowchart TB
    classDef domain fill:#FF00FF,stroke:#000000,stroke-width:3px,color:#000000,font-weight:bold
    classDef implemented fill:#00FF00,stroke:#000000,stroke-width:2px,color:#000000,font-weight:bold
    classDef reported fill:#00FFFF,stroke:#000000,stroke-width:2px,color:#000000,font-weight:bold
    classDef experimental fill:#FFD700,stroke:#000000,stroke-width:2px,color:#000000,font-weight:bold
    classDef planned fill:#FFA500,stroke:#000000,stroke-width:2px,color:#000000,font-weight:bold

    ROOT["Part 5: Comparison / Key Gaps / Status Legend"]:::domain

    subgraph CMP["Comparison"]
        CMP1["Our AST model rank: 1 of 8<br/>Source: PWA README<br/>Status: Reported"]:::reported
        CMP2["FunnelNet spec/acc: 0.920 / 85.0%<br/>Source: PWA README<br/>Status: Reported"]:::reported
        CMP3["CardioSense AUC: 0.8041<br/>Source: PWA README<br/>Status: Reported"]:::reported
        CMP4["ai-mitra accuracy: 76.5%<br/>Source: PWA README<br/>Status: Reported"]:::reported
        CMP5["Hemg accuracy: 100% overfit<br/>Source: PWA README<br/>Status: Reported"]:::reported
    end

    subgraph GAP["Key Gaps"]
        GAP1["True cross-device P2P: not validated<br/>Status: Planned / Not validated"]:::planned
        GAP2["Real human correction learning: not validated<br/>Status: Planned / Not validated"]:::planned
        GAP3["Clinical validation: not performed<br/>Status: Planned / Not validated"]:::planned
        GAP4["License confirmation for HF: needs verification<br/>Status: Planned / Not validated"]:::planned
        GAP5["Ablation study: planned<br/>Status: Planned / Not validated"]:::planned
    end

    subgraph LEG["Status Legend"]
        L1["Implemented: Code exists and runs"]:::implemented
        L2["Reported: Value reported; verify source/reproducibility"]:::reported
        L3["Experimental: Implemented but not adequately validated"]:::experimental
        L4["Planned / Not validated: Not yet tested or validated"]:::planned
    end

    ROOT --> CMP
    ROOT --> GAP
    ROOT --> LEG
    CMP --> GAP
```
```