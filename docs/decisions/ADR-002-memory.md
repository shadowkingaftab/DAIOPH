# ADR-002: Multi-Tier Memory with Consolidation

## Status

Accepted

## Context

An adaptive assistant needs memory that mirrors human cognition:
- Immediate conversational context (seconds)
- Recent interaction history (hours/days)
- Long-term knowledge and preferences (months/years)

Requirements:
1. Fast retrieval for context building (< 50ms)
2. Persistence across restarts
3. Privacy: all data local by default, encrypted at rest
4. Bounded storage on edge devices
5. Support for semantic similarity search

Alternatives considered:
- **Single vector database**: Simple but conflates timescales; no forgetting semantics
- **Pure LLM context window**: No persistence; expensive; limited capacity
- **Relational-only**: Poor semantic search without embeddings

## Decision

Implement a **multi-tier memory system** (`memory/`) inspired by cognitive science:

| Tier | Store | Lifetime | Backend |
|------|-------|----------|---------|
| Short-term | Conversation buffer + working context | Session | In-memory |
| Episodic | Timestamped episodes | Weeks–months | SQLite/Postgres |
| Semantic | Facts + concepts | Indefinite | SQLite + FAISS |
| Procedural | Skills + workflows | Indefinite | SQLite |
| Preference | User preferences | Indefinite | SQLite |

Key mechanisms:

1. **Consolidation pipeline** (`memory/consolidation/`): periodically promotes short-term → episodic → semantic, with deduplication and importance scoring
2. **Forgetting policy**: bounded storage via importance-weighted eviction
3. **Vector index** (FAISS) over all tiers for semantic retrieval
4. **Knowledge graph** for entity/relation queries alongside vectors
5. **Encryption** of sensitive memories at rest

## Consequences

### Positive
- Natural mapping from cognitive theory to implementation
- Each tier can be tuned independently per device profile
- Forgetting is principled (importance-based), not arbitrary truncation
- Vector + graph gives both similarity and structured query power

### Negative
- More moving parts than a single store
- Consolidation adds background CPU load (throttled on edge)
- Migration complexity across schema versions

### Neutral
- Storage backends are swappable (SQLite ↔ Postgres) behind a common interface