# ADR-004: Federated Learning with Differential Privacy

## Status

Accepted

## Context

DAIOPH devices generate valuable training signal (user preferences, task patterns, corrections), but:

1. **Privacy**: Raw interaction data must never leave the device
2. **Heterogeneity**: Devices range from Pi to GPU servers; data distributions differ per user (non-IID)
3. **Adversarial risk**: Malicious clients could poison the global model
4. **Connectivity**: Edge devices are often offline; participation is opportunistic

Alternatives considered:
- **Centralized training**: Requires raw data upload — violates privacy principle
- **No learning sharing**: Each device learns alone; slower improvement, no collective benefit
- **Trusted aggregation only (no DP)**: Server still sees individual updates; insufficient

## Decision

Implement **federated learning** (`federated/`) with layered privacy and robustness:

### 1. Federated Averaging (FedAvg)
- Clients train locally for N epochs per round
- Server aggregates weighted by client data size
- Momentum variant for faster convergence

### 2. Differential Privacy (DP-SGD)
- Gradient clipping to bound per-sample sensitivity
- Gaussian noise calibrated to (ε=1.0, δ=1e-5) budget
- Privacy accountant tracks cumulative loss (RDP accounting)

### 3. Secure Aggregation
- Cryptographic masking: server sees only the sum of updates
- Minimum 3 clients required per round
- Individual updates are never reconstructable

### 4. Poisoning Defenses (`federated/reputation/`)
- Norm clipping bounds update magnitude
- Cosine similarity check against historical update direction
- Outlier rejection before aggregation
- Reputation scoring down-weights unreliable clients over time

### 5. Opportunistic Participation
Clients join rounds when eligible:
- Sufficient battery (>20%)
- On WiFi (configurable)
- Idle (not degrading user experience)

## Consequences

### Positive
- Collective model improvement without privacy sacrifice
- Non-IID tolerance via local adaptation + FedAvg
- Poisoning resistance through layered defenses
- Works with intermittent connectivity

### Negative
- DP noise reduces model accuracy (~5–15% depending on ε)
- Secure aggregation adds communication overhead
- Round coordination complexity; stragglers delay rounds
- Debugging aggregated failures is harder (updates are opaque)

### Neutral
- Federation is optional per deployment; fully offline operation unaffected
- Adapter-based updates (LoRA) keep communication small enough for mobile networks