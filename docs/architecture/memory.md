# Memory Architecture

## Overview

DAIOPH implements a multi-tier memory system inspired by human cognition, with specialized stores for different types of information and timescales.

## Memory Types

### Short-Term Memory (`memory/short_term/`)
- **Conversation Buffer**: Recent dialogue turns
- **Working Context**: Active task context
- TTL-based expiration, in-memory storage

### Episodic Memory (`memory/episodic/`)
- **Episodic Memory**: Timestamped interaction episodes
- **Event Store**: Append-only event log
- **Episode Index**: Fast retrieval by time/content
- Supports "what happened when" queries

### Semantic Memory (`memory/semantic/`)
- **Semantic Memory**: Facts and knowledge
- **Knowledge Store**: Structured knowledge entries
- **Concept Index**: Concept-based lookup
- Long-term factual knowledge

### Procedural Memory (`memory/procedural/`)
- **Skill Store**: Learned skills and capabilities
- **Workflow Store**: Multi-step procedures
- "How to do X" knowledge

### Preference Memory (`memory/preference/`)
- **Preference Memory**: User preferences
- **Preference Model**: Learned preference patterns
- **Preference Updater**: Incremental updates

## Vector & Graph Stores

### Vector Store (`memory/vector/`)
- **FAISS Store**: High-performance similarity search
- **Embedding Store**: Embedding management
- Used for semantic retrieval across all memory types

### Knowledge Graph (`memory/graph/`)
- **Entity Graph**: Entities and their attributes
- **Relation Store**: Typed relationships
- **Graph Query**: Traversal and pattern matching

## Consolidation (`memory/consolidation/`)

The consolidator moves information between tiers:
- **Deduplicator**: Removes redundant entries
- **Importance Scorer**: Ranks memories by relevance
- **Forgetting Policy**: Prunes low-value memories

```
Short-term ──(consolidate)──→ Episodic ──(extract)──→ Semantic
                                    │
                                    └──(generalize)──→ Procedural
```

## Storage Backends (`memory/storage/`)
- **SQLite Store**: Default local storage
- **Postgres Store**: Production deployments
- **Object Store**: Large binary artifacts
- **Migrations**: Schema versioning

## Privacy (`memory/privacy/`)
- **Encryption**: At-rest encryption of sensitive memories
- Key management via device identity