# Federated Learning Experiments

## Experiment Log

| ID | Date | Experiment | Status | Result |
|----|------|-----------|--------|--------|
| FL-001 | 2026-08 | DP budget vs. accuracy trade-off | Planned | — |
| FL-002 | 2026-08 | Secure aggregation overhead | Planned | — |
| FL-003 | 2026-08 | Poisoning attack defense | Planned | — |
| FL-004 | 2026-08 | Non-IID heterogeneity handling | Planned | — |

## FL-001: DP Budget vs. Accuracy Trade-off

**Hypothesis**: ε=1.0 costs 5–15% accuracy relative to non-private training; ε=4.0 costs <5%.

**Setup**:
- Intent classification task, 20 simulated clients
- ε ∈ {0.5, 1.0, 2.0, 4.0, ∞}
- Measure: global model accuracy per round, privacy spent

**Protocol**:
```bash
python experiments/federated/run_dp_tradeoff.py --epsilon 0.5
python experiments/federated/run_dp_tradeoff.py --epsilon 1.0
python experiments/federated/run_dp_tradeoff.py --epsilon 4.0
```

**Results**: TBD

## FL-002: Secure Aggregation Overhead

**Hypothesis**: Secure aggregation adds <10% round time for ≤100 clients.

**Setup**:
- Vary client count: 3, 10, 50, 100
- Compare: plain aggregation vs. masked aggregation
- Metrics: wall-clock round time, bandwidth per client

**Results**: TBD

## FL-003: Poisoning Attack Defense

**Hypothesis**: Norm clipping + cosine similarity catches label-flipping and backdoor attacks with >95% detection and <2% false positives.

**Threat models tested**:
1. Label flipping (30% malicious clients)
2. Backdoor insertion via crafted updates
3. Model replacement attack

**Metrics**: detection rate, false positive rate, global model integrity after defense.

**Results**: TBD

## FL-004: Non-IID Heterogeneity Handling

**Hypothesis**: Local adaptation + FedAvg outperforms pure FedAvg on non-IID data by ≥10%.

**Setup**:
- Simulate Dirichlet-distributed data partitions (α = 0.1, 0.5)
- Compare: FedAvg, FedProx, local-adapt + FedAvg
- Metrics: convergence rounds, final accuracy

**Results**: TBD

## Methodology Notes

- All attacks are simulated in isolated environments only
- Client simulation uses realistic network delay distributions
- Privacy accounting verified against reference implementations