# Federation Architecture

## Overview

Federated learning enables DAIOPH devices to collaboratively improve models without sharing raw data. Each device trains locally; only privacy-protected model updates are shared.

## Architecture

```
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Client A │  │ Client B │  │ Client C │
│ (local   │  │ (local   │  │ (local   │
│ training)│  │ training)│  │ training)│
└────┬─────┘  └────┬─────┘  └────┬─────┘
     │ DP update   │ DP update   │ DP update
     ▼             ▼             ▼
┌─────────────────────────────────────────┐
│         Federated Server                │
│  (Aggregation / Validation / Rounds)    │
└──────────────────┬──────────────────────┘
                   │ Global model
                   ▼
            All clients updated
```

## Client Components (`federated/client/`)

### Client (`client.py`)
- Registers with server
- Participates in rounds when eligible
- Applies global model updates

### Local Training (`local_training.py`)
- Trains on-device for N epochs per round
- Uses local interaction data only

### Update Builder (`update_builder.py`)
- Computes weight deltas
- Applies differential privacy noise
- Clips gradients to bound sensitivity

### Contribution (`contribution.py`)
- Tracks client contribution quality
- Feeds reputation scoring

## Server Components (`federated/server/`)

### Server & Coordinator
- Manages round lifecycle
- Selects participating clients
- Distributes global model

### Aggregation (`aggregation.py`)
- **FedAvg**: Weighted average by data size
- Supports momentum-based variants

### Validation (`validation.py`)
- Rejects malformed updates
- Outlier detection before aggregation

## Privacy (`federated/privacy/`)

### Differential Privacy (`differential_privacy.py`)
- DP-SGD: Gaussian noise + gradient clipping
- Configurable ε (privacy budget) and δ
- Typical settings: ε=1.0, δ=1e-5

### Secure Aggregation (`secure_aggregation.py`)
- Cryptographic masking so server sees only the sum
- Requires minimum client count per round

### Privacy Accountant (`privacy_accountant.py`)
- Tracks cumulative privacy loss (RDP accounting)
- Enforces budget limits per client

## Reputation & Trust (`federated/reputation/`)

- **Contribution Score**: Quality of each client's updates
- **Trust**: Long-term reliability measure
- Low-trust clients get reduced influence

## Poisoning Detection (`poisoning_detection.py`)

Defenses against malicious updates:
- Norm clipping (bounds update magnitude)
- Cosine similarity checks vs. historical direction
- Outlier rejection before aggregation

## Protocol (`federated/protocol/`)

- **Messages**: Round request/response formats
- **Rounds**: Round state machine
- **Versioning**: Model version compatibility

## Configuration

See `configs/federated/client.yaml` and `configs/federated/server.yaml`.