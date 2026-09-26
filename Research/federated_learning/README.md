# Federated Learning Research

## Overview

Research on privacy-preserving collaborative learning across DAIOPH devices: FedAvg variants, differential privacy trade-offs, secure aggregation, and poisoning resistance.

## Research Questions

1. What accuracy cost does DP-SGD impose at various ε budgets?
2. How does secure aggregation affect convergence speed?
3. Which poisoning defenses catch realistic attacks with minimal false positives?
4. How should heterogeneous devices be weighted in aggregation?

## Key Components Under Study

- `Backend/federated/server/aggregation.py` — FedAvg and variants
- `Backend/federated/privacy/differential_privacy.py` — DP-SGD
- `Backend/federated/privacy/secure_aggregation.py` — cryptographic masking
- `Backend/federated/reputation/poisoning_detection.py` — attack defense
- `Backend/federated/privacy/privacy_accountant.py` — budget tracking

## Related Documentation

- Architecture: `Documentation/docs/architecture/federation.md`
- Decision record: `Documentation/docs/decisions/ADR-004-federation.md`
- Experiments: [experiments.md](experiments.md)

## Getting Started

```bash
python Research/experiments/Backend/federated/run_dp_tradeoff.py --epsilon 1.0
```

## Contributing

Attack simulations must be documented with threat models. Never test against production servers.