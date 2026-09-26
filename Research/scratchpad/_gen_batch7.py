
"""Batch 7 generator: Backend/knowledge/, Backend/learning/, Backend/models/liquid/ implementations."""
from __future__ import annotations

import pathlib

FILES: dict[str, str] = {}

# ---------------------------------------------------------------- Backend/knowledge/__init__
FILES["Backend/knowledge/__init__.py"] = '''"""Knowledge layer: ingestion, indexing, retrieval, ontology, provenance."""
'''

FILES["Backend/knowledge/indexing/__init__.py"] = '''"""Indexing subsystem: lexical, vector, semantic, and graph indexes."""
'''

FILES["Backend/knowledge/retrieval/__init__.py"] = '''"""Retrieval subsystem: retrievers, hybrid search, reranking, context."""
'''

FILES["Backend/knowledge/ontology/__init__.py"] = '''"""Ontology subsystem: entities, relations, class hierarchy, reasoning."""
'''

FILES["Backend/knowledge/provenance/__init__.py"] = '''"""Provenance subsystem: sources, citations, evidence, lineage."""
'''

# ---------------------------------------------------------------- Backend/knowledge/indexing
FILES["Backend/knowledge/indexing/lexical_index.py"] = '''"""Lexical inverted index with deterministic TF scoring."""

from __future__ import annotations

import math
import re
from collections import Counter
from typing import Dict, List, Tuple

__all__ = ["LexicalIndex", "tokenize"]

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> List[str]:
    """Lowercase word-boundary tokenization."""
    return _TOKEN_RE.findall(text.lower())


class LexicalIndex:
    """Inverted index over documents with TF-IDF-free TF scoring.

    Deterministic: scores depend only on inserted documents and the query.
    """

    def __init__(self) -> None:
        self._docs: Dict[str, str] = {}
        self._postings: Dict[str, Dict[str, int]] = {}

    def add(self, doc_id: str, text: str) -> None:
        """Index *text* under *doc_id* (re-indexing replaces the old text)."""
        if doc_id in self._docs:
            self.remove(doc_id)
        self._docs[doc_id] = text
        for token, count in Counter(tokenize(text)).items():
            self._postings.setdefault(token, {})[doc_id] = count

    def remove(self, doc_id: str) -> None:
        """Remove a document from the index (no-op if absent)."""
        text = self._docs.pop(doc_id, None)
        if text is None:
            return
        for token in tokenize(text):
            docs = self._postings.get(token)
            if docs is not None:
                docs.pop(doc_id, None)
                if not docs:
                    del self._postings[token]

    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Return (doc_id, score) pairs sorted by descending TF score.

        Score is the sum over query terms of log(1 + tf). Documents
        matching more query terms and with higher term frequency rank first.
        """
        if top_k < 1:
            raise ValueError("top_k must be >= 1")
        scores: Dict[str, float] = {}
        for token in tokenize(query):
            for doc_id, tf in self._postings.get(token, {}).items():
                scores[doc_id] = scores.get(doc_id, 0.0) + math.log1p(tf)
        ranked = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
        return ranked[:top_k]

    def __len__(self) -> int:
        return len(self._docs)

    def doc_ids(self) -> List[str]:
        """All indexed document ids in insertion order."""
        return list(self._docs)
'''

FILES["Backend/knowledge/indexing/vector_index.py"] = '''"""Vector index with cosine similarity and an injected embedder."""

from __future__ import annotations

import math
from typing import Callable, Dict, List, Optional, Sequence, Tuple

__all__ = ["VectorIndex", "cosine_similarity"]

EmbedFn = Callable[[str], Sequence[float]]


def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    """Cosine similarity between two equal-length vectors."""
    if len(a) != len(b):
        raise ValueError("vectors must have equal length")
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)


class VectorIndex:
    """Flat vector store. Embeddings come from an injected embedder.

    The embedder is a callable mapping text -> vector; no ML library is
    required. Callers may inject any deterministic embedding function.
    """

    def __init__(self, embedder: Optional[EmbedFn] = None) -> None:
        self._embedder = embedder
        self._vectors: Dict[str, Sequence[float]] = {}
        self._texts: Dict[str, str] = {}

    def set_embedder(self, embedder: EmbedFn) -> None:
        """Set or replace the embedder used for future additions/queries."""
        self._embedder = embedder

    def _require_embedder(self) -> EmbedFn:
        if self._embedder is None:
            raise RuntimeError("no embedder configured; call set_embedder()")
        return self._embedder

    def add(self, doc_id: str, text: str) -> None:
        """Embed and store *text* under *doc_id*."""
        self._vectors[doc_id] = tuple(self._require_embedder()(text))
        self._texts[doc_id] = text

    def remove(self, doc_id: str) -> None:
        """Remove a document (no-op if absent)."""
        self._vectors.pop(doc_id, None)
        self._texts.pop(doc_id, None)

    def search(
        self, query: str, top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """Return (doc_id, cosine similarity) sorted by descending score."""
        if top_k < 1:
            raise ValueError("top_k must be >= 1")
        qv = tuple(self._require_embedder()(query))
        scored = [
            (doc_id, cosine_similarity(qv, vec))
            for doc_id, vec in self._vectors.items()
        ]
        scored.sort(key=lambda kv: (-kv[1], kv[0]))
        return scored[:top_k]

    def text(self, doc_id: str) -> Optional[str]:
        """Stored text for *doc_id*, or None."""
        return self._texts.get(doc_id)

    def __len__(self) -> int:
        return len(self._vectors)
'''

FILES["Backend/knowledge/indexing/semantic_index.py"] = '''"""Semantic index: vector index plus optional lexical fallback merge."""

from __future__ import annotations

from typing import Callable, Dict, List, Optional, Tuple

from knowledge.indexing.lexical_index import LexicalIndex
from knowledge.indexing.vector_index import VectorIndex

__all__ = ["SemanticIndex"]

EmbedFn = Callable[[str], "Sequence[float]"]  # noqa: F821


class SemanticIndex:
    """Combines a vector index (primary) with a lexical index (fallback).

    When the embedder yields an all-zero vector (no signal), lexical
    results are returned instead so retrieval never silently degrades.
    """

    def __init__(self, embedder: Optional[EmbedFn] = None) -> None:
        self.vector = VectorIndex(embedder)
        self.lexical = LexicalIndex()

    def set_embedder(self, embedder: EmbedFn) -> None:
        """Set the embedder on the underlying vector index."""
        self.vector.set_embedder(embedder)

    def add(self, doc_id: str, text: str) -> None:
        """Add a document to both underlying indexes."""
        self.vector.add(doc_id, text)
        self.lexical.add(doc_id, text)

    def remove(self, doc_id: str) -> None:
        """Remove a document from both underlying indexes."""
        self.vector.remove(doc_id)
        self.lexical.remove(doc_id)

    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Search semantically; fall back to lexical when vectors are flat."""
        if top_k < 1:
            raise ValueError("top_k must be >= 1")
        results = self.vector.search(query, top_k=top_k)
        if results and all(score == 0.0 for _, score in results):
            return self.lexical.search(query, top_k=top_k)
        return results

    def __len__(self) -> int:
        return len(self.vector)
'''

FILES["Backend/knowledge/indexing/graph_index.py"] = '''"""Directed graph index with neighbor lookup and BFS shortest paths."""

from __future__ import annotations

from collections import deque
from typing import Dict, Hashable, List, Optional, Set, Tuple

__all__ = ["GraphIndex"]

Node = Hashable


class GraphIndex:
    """Directed multigraph over hashable nodes with deterministic order."""

    def __init__(self) -> None:
        self._edges: Dict[Node, List[Node]] = {}
        self._nodes: List[Node] = []
        self._node_set: Set[Node] = set()

    def add_node(self, node: Node) -> None:
        """Add an isolated node (no-op if present)."""
        if node not in self._node_set:
            self._node_set.add(node)
            self._nodes.append(node)
            self._edges.setdefault(node, [])

    def add_edge(self, src: Node, dst: Node) -> None:
        """Add a directed edge, creating nodes as needed."""
        self.add_node(src)
        self.add_node(dst)
        outs = self._edges[src]
        if dst not in outs:
            outs.append(dst)

    def has_edge(self, src: Node, dst: Node) -> bool:
        """True when a directed edge src -> dst exists."""
        return dst in self._edges.get(src, [])

    def neighbors(self, node: Node) -> List[Node]:
        """Out-neighbors in insertion order."""
        return list(self._edges.get(node, []))

    def nodes(self) -> List[Node]:
        """All nodes in insertion order."""
        return list(self._nodes)

    def shortest_path(self, src: Node, dst: Node) -> Optional[List[Node]]:
        """BFS shortest path from src to dst, or None if unreachable."""
        if src not in self._node_set or dst not in self._node_set:
            return None
        if src == dst:
            return [src]
        visited = {src}
        queue: deque = deque([(src, [src])])
        while queue:
            current, path = queue.popleft()
            for nxt in self._edges.get(current, []):
                if nxt in visited:
                    continue
                if nxt == dst:
                    return path + [nxt]
                visited.add(nxt)
                queue.append((nxt, path + [nxt]))
        return None

    def reachable(self, src: Node) -> Set[Node]:
        """All nodes reachable from *src* (excluding src unless cyclic)."""
        if src not in self._node_set:
            return set()
        visited: Set[Node] = set()
        stack = [src]
        while stack:
            current = stack.pop()
            for nxt in self._edges.get(current, []):
                if nxt not in visited:
                    visited.add(nxt)
                    stack.append(nxt)
        return visited

    def __len__(self) -> int:
        return len(self._nodes)
'''

# ---------------------------------------------------------------- Backend/knowledge/retrieval
FILES["Backend/knowledge/retrieval/retriever.py"] = '''"""Generic retriever over any index exposing search()."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Protocol, Tuple

__all__ = ["Retriever", "Hit", "SupportsSearch"]


class SupportsSearch(Protocol):
    """Anything with search(query, top_k) -> list of (id, score)."""

    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        ...  # pragma: no cover


@dataclass(frozen=True)
class Hit:
    """A single retrieval hit."""

    doc_id: str
    score: float


class Retriever:
    """Thin wrapper adding score normalization and hit objects."""

    def __init__(self, index: SupportsSearch) -> None:
        self._index = index

    def retrieve(self, query: str, top_k: int = 5) -> List[Hit]:
        """Retrieve top_k hits for *query*."""
        if top_k < 1:
            raise ValueError("top_k must be >= 1")
        return [
            Hit(doc_id=str(doc_id), score=float(score))
            for doc_id, score in self._index.search(query, top_k=top_k)
        ]

    def retrieve_normalized(self, query: str, top_k: int = 5) -> List[Hit]:
        """Hits with scores scaled to [0, 1] by the max score (if > 0)."""
        hits = self.retrieve(query, top_k=top_k)
        peak = max((h.score for h in hits), default=0.0)
        if peak <= 0.0:
            return hits
        return [
            Hit(doc_id=h.doc_id, score=h.score / peak) for h in hits
        ]
'''

FILES["Backend/knowledge/retrieval/hybrid_search.py"] = '''"""Hybrid search: weighted merge of lexical and vector results."""

from __future__ import annotations

from typing import Dict, List, Tuple

from knowledge.indexing.lexical_index import LexicalIndex
from knowledge.indexing.vector_index import VectorIndex

__all__ = ["hybrid_search"]


def _normalize(pairs: List[Tuple[str, float]]) -> Dict[str, float]:
    peak = max((s for _, s in pairs), default=0.0)
    if peak <= 0.0:
        return {doc_id: 0.0 for doc_id, _ in pairs}
    return {doc_id: s / peak for doc_id, s in pairs}


def hybrid_search(
    lexical: LexicalIndex,
    vector: VectorIndex,
    query: str,
    top_k: int = 5,
    lexical_weight: float = 0.5,
) -> List[Tuple[str, float]]:
    """Merge lexical and vector rankings with a weighted linear score.

    Both result lists are min-max normalized to [0, 1] by their own peak
    score, then combined as ``w * lexical + (1 - w) * vector``. Ties break
    by doc id for determinism.
    """
    if top_k < 1:
        raise ValueError("top_k must be >= 1")
    if not 0.0 <= lexical_weight <= 1.0:
        raise ValueError("lexical_weight must be within [0, 1]")
    lex = _normalize(lexical.search(query, top_k=top_k * 2))
    vec = _normalize(vector.search(query, top_k=top_k * 2))
    combined: Dict[str, float] = {}
    for doc_id in set(lex) | set(vec):
        combined[doc_id] = (
            lexical_weight * lex.get(doc_id, 0.0)
            + (1.0 - lexical_weight) * vec.get(doc_id, 0.0)
        )
    ranked = sorted(combined.items(), key=lambda kv: (-kv[1], kv[0]))
    return ranked[:top_k]
'''

FILES["Backend/knowledge/retrieval/reranker.py"] = '''"""Reranking utilities over candidate documents."""

from __future__ import annotations

from typing import Callable, List, Sequence, Tuple

__all__ = ["rerank", "keyword_overlap_scorer"]

Doc = Tuple[str, str]  # (doc_id, text)
Scorer = Callable[[str, str], float]


def keyword_overlap_scorer(query: str, text: str) -> float:
    """Fraction of query keywords present in *text* (case-insensitive)."""
    q_words = {w for w in query.lower().split() if w}
    if not q_words:
        return 0.0
    t_words = set(text.lower().split())
    return len(q_words & t_words) / len(q_words)


def rerank(
    query: str,
    docs: Sequence[Doc],
    scorer: Scorer = keyword_overlap_scorer,
    top_k: int = 5,
) -> List[Tuple[str, float]]:
    """Score each (doc_id, text) with *scorer* and return the best top_k.

    Deterministic: ties break by doc id ascending.
    """
    if top_k < 1:
        raise ValueError("top_k must be >= 1")
    scored = [(doc_id, float(scorer(query, text))) for doc_id, text in docs]
    scored.sort(key=lambda kv: (-kv[1], kv[0]))
    return scored[:top_k]
'''

FILES["Backend/knowledge/retrieval/context_builder.py"] = '''"""Context builder: assemble retrieved snippets into a bounded prompt."""

from __future__ import annotations

from typing import Iterable, List, Sequence

__all__ = ["build_context", "ContextSnippet"]


class ContextSnippet:
    """A labeled snippet of text for context assembly."""

    __slots__ = ("doc_id", "text")

    def __init__(self, doc_id: str, text: str) -> None:
        self.doc_id = doc_id
        self.text = text

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"ContextSnippet(doc_id={self.doc_id!r})"


def build_context(
    snippets: Sequence[ContextSnippet], max_chars: int = 2000
) -> str:
    """Join snippets as ``[doc_id] text`` blocks within a character budget.

    Snippets are included in order until the budget is exhausted; a snippet
    that does not fit is truncated to the remaining space. At least one
    snippet is always included (possibly truncated) when any are given.
    """
    if max_chars < 1:
        raise ValueError("max_chars must be >= 1")
    blocks: List[str] = []
    used = 0
    for snip in snippets:
        header = f"[{snip.doc_id}] "
        allowance = max_chars - used - len(header)
        if allowance <= 0 and blocks:
            break
        body = snip.text[: max(allowance, 1)]
        block = header + body
        blocks.append(block)
        used += len(block) + 1  # +1 for the joining newline
        if used >= max_chars:
            break
    return "\\n".join(blocks)
'''

# ---------------------------------------------------------------- Backend/knowledge/ontology
FILES["Backend/knowledge/ontology/entities.py"] = '''"""Entities and an entity store."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

__all__ = ["Entity", "EntityStore"]


@dataclass(frozen=True)
class Entity:
    """A named entity with an ontology type and free-form attributes."""

    entity_id: str
    name: str
    entity_type: str
    attributes: Dict[str, str] = field(default_factory=dict)


class EntityStore:
    """Insertion-ordered store of entities keyed by id."""

    def __init__(self) -> None:
        self._entities: Dict[str, Entity] = {}

    def add(self, entity: Entity) -> Entity:
        """Add an entity; raises ValueError on duplicate id."""
        if entity.entity_id in self._entities:
            raise ValueError(f"duplicate entity id: {entity.entity_id!r}")
        self._entities[entity.entity_id] = entity
        return entity

    def get(self, entity_id: str) -> Optional[Entity]:
        """Fetch an entity by id, or None."""
        return self._entities.get(entity_id)

    def require(self, entity_id: str) -> Entity:
        """Fetch an entity or raise KeyError."""
        try:
            return self._entities[entity_id]
        except KeyError:
            raise KeyError(f"unknown entity: {entity_id!r}") from None

    def by_type(self, entity_type: str) -> List[Entity]:
        """All entities of *entity_type* in insertion order."""
        return [
            e for e in self._entities.values() if e.entity_type == entity_type
        ]

    def find_by_name(self, name: str) -> List[Entity]:
        """Case-insensitive name lookup."""
        lowered = name.lower()
        return [e for e in self._entities.values() if e.name.lower() == lowered]

    def __len__(self) -> int:
        return len(self._entities)
'''

FILES["Backend/knowledge/ontology/relations.py"] = '''"""Typed relations between entities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

__all__ = ["Relation", "RelationStore"]


@dataclass(frozen=True)
class Relation:
    """A directed, typed relation: subject -predicate-> object."""

    subject: str
    predicate: str
    object: str


class RelationStore:
    """Store of relations with indexed lookups by subject and object."""

    def __init__(self) -> None:
        self._relations: List[Relation] = []
        self._by_subject: Dict[str, List[Relation]] = {}
        self._by_object: Dict[str, List[Relation]] = {}

    def add(self, relation: Relation) -> Relation:
        """Add a relation (duplicate triples are ignored)."""
        if relation not in self._relations:
            self._relations.append(relation)
            self._by_subject.setdefault(relation.subject, []).append(relation)
            self._by_object.setdefault(relation.object, []).append(relation)
        return relation

    def by_subject(
        self, subject: str, predicate: Optional[str] = None
    ) -> List[Relation]:
        """Relations with *subject*, optionally filtered by predicate."""
        rels = self._by_subject.get(subject, [])
        if predicate is None:
            return list(rels)
        return [r for r in rels if r.predicate == predicate]

    def by_object(
        self, obj: str, predicate: Optional[str] = None
    ) -> List[Relation]:
        """Relations with *object*, optionally filtered by predicate."""
        rels = self._by_object.get(obj, [])
        if predicate is None:
            return list(rels)
        return [r for r in rels if r.predicate == predicate]

    def all_relations(self) -> List[Relation]:
        """All relations in insertion order."""
        return list(self._relations)

    def objects_of(self, subject: str, predicate: str) -> List[str]:
        """Object ids for (subject, predicate) pairs."""
        return [r.object for r in self.by_subject(subject, predicate)]

    def subjects_of(self, obj: str, predicate: str) -> List[str]:
        """Subject ids for (predicate, object) pairs."""
        return [r.subject for r in self.by_object(obj, predicate)]

    def __len__(self) -> int:
        return len(self._relations)
'''

FILES["Backend/knowledge/ontology/ontology.py"] = '''"""Ontology: class hierarchy with subclass closure."""

from __future__ import annotations

from typing import Dict, Iterable, List, Set

__all__ = ["Ontology"]


class Ontology:
    """A set of classes with ``subclass_of`` edges and closure queries."""

    def __init__(self) -> None:
        self._parents: Dict[str, List[str]] = {}
        self._classes: List[str] = []
        self._class_set: Set[str] = set()

    def add_class(self, name: str) -> None:
        """Register a class (no-op if present)."""
        if name not in self._class_set:
            self._class_set.add(name)
            self._classes.append(name)
            self._parents.setdefault(name, [])

    def add_subclass(self, child: str, parent: str) -> None:
        """Declare child is-a parent (both classes registered as needed)."""
        self.add_class(child)
        self.add_class(parent)
        parents = self._parents[child]
        if parent not in parents:
            parents.append(parent)

    def classes(self) -> List[str]:
        """All classes in insertion order."""
        return list(self._classes)

    def direct_parents(self, name: str) -> List[str]:
        """Immediate parents of *name*."""
        return list(self._parents.get(name, []))

    def ancestors(self, name: str) -> Set[str]:
        """All transitive parents of *name* (excluding name itself)."""
        seen: Set[str] = set()
        stack = list(self._parents.get(name, []))
        while stack:
            current = stack.pop()
            if current in seen:
                continue
            seen.add(current)
            stack.extend(self._parents.get(current, []))
        return seen

    def is_a(self, child: str, parent: str) -> bool:
        """True when child is parent or a transitive subclass."""
        if child == parent:
            return child in self._class_set
        return parent in self.ancestors(child)

    def descendants(self, parent: str) -> Set[str]:
        """All classes that are (transitively) subclasses of *parent*."""
        result: Set[str] = set()
        for name in self._classes:
            if name != parent and parent in self.ancestors(name):
                result.add(name)
        return result
'''

FILES["Backend/knowledge/ontology/reasoning.py"] = '''"""Lightweight ontology reasoning: transitivity and path queries."""

from __future__ import annotations

from typing import Dict, List, Optional

from knowledge.ontology.relations import Relation, RelationStore

__all__ = ["infer_transitive", "explain_relation"]


def infer_transitive(
    store: RelationStore, predicate: str, max_depth: int = 8
) -> Dict[str, List[str]]:
    """Infer transitive closure of *predicate* over the relation store.

    For example, with predicate ``"part_of"`` the result maps each subject
    to every object reachable through one or more ``part_of`` hops.
    """
    if max_depth < 1:
        raise ValueError("max_depth must be >= 1")
    closure: Dict[str, List[str]] = {}
    # Build adjacency once for determinism and speed.
    adjacency: Dict[str, List[str]] = {}
    for rel in store.all_relations():
        if rel.predicate == predicate:
            adjacency.setdefault(rel.subject, []).append(rel.object)

    def walk(start: str) -> List[str]:
        seen: List[str] = []
        frontier = [start]
        for _ in range(max_depth):
            nxt: List[str] = []
            for node in frontier:
                for target in adjacency.get(node, []):
                    if target == start or target in seen:
                        continue
                    seen.append(target)
                    nxt.append(target)
            if not nxt:
                break
            frontier = nxt
        return seen

    for subject in sorted(adjacency):
        closure[subject] = walk(subject)
    return closure


def explain_relation(
    store: RelationStore, subject: str, obj: str, predicate: str
) -> Optional[List[Relation]]:
    """Return a hop-by-hop relation chain subject -> ... -> obj, or None.

    Breadth-first over *predicate* edges; the first found chain is
    returned (deterministic given insertion order).
    """
    if subject == obj:
        return []
    frontier: List[List[Relation]] = [
        [r] for r in store.by_subject(subject, predicate)
    ]
    visited = {subject}
    while frontier:
        chain = frontier.pop(0)
        tail = chain[-1].object
        if tail == obj:
            return chain
        if tail in visited:
            continue
        visited.add(tail)
        for rel in store.by_subject(tail, predicate):
            frontier.append(chain + [rel])
    return None
'''

# ---------------------------------------------------------------- Backend/knowledge/provenance
FILES["Backend/knowledge/provenance/source.py"] = '''"""Provenance sources."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

__all__ = ["Source"]


@dataclass(frozen=True)
class Source:
    """Where a piece of knowledge came from.

    Attributes:
        source_id: Stable identifier.
        uri: Locator (URL, path, or other scheme).
        retrieved_at: Unix timestamp of retrieval (0 if unknown).
        trust: Trust score in [0, 1]; 0.5 by default.
        metadata: Arbitrary extra provenance data.
    """

    source_id: str
    uri: str
    retrieved_at: int = 0
    trust: float = 0.5
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not 0.0 <= self.trust <= 1.0:
            raise ValueError("trust must be within [0, 1]")
'''

FILES["Backend/knowledge/provenance/citation.py"] = '''"""Citations linking statements back to sources."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from knowledge.provenance.source import Source

__all__ = ["Citation", "CitationRegistry"]


@dataclass(frozen=True)
class Citation:
    """A statement attributed to one source."""

    statement: str
    source_id: str


class CitationRegistry:
    """Registry of sources and citations with formatted output."""

    def __init__(self) -> None:
        self._sources: Dict[str, Source] = {}
        self._citations: List[Citation] = []

    def register_source(self, source: Source) -> Source:
        """Register a source (duplicate ids raise ValueError)."""
        if source.source_id in self._sources:
            raise ValueError(f"duplicate source id: {source.source_id!r}")
        self._sources[source.source_id] = source
        return source

    def cite(self, statement: str, source_id: str) -> Citation:
        """Record a citation; the source must already be registered."""
        if source_id not in self._sources:
            raise KeyError(f"unknown source: {source_id!r}")
        citation = Citation(statement=statement, source_id=source_id)
        self._citations.append(citation)
        return citation

    def format(self, citation: Citation) -> str:
        """Human-readable citation string."""
        source = self._sources[citation.source_id]
        return f'"{citation.statement}" [{source.source_id}: {source.uri}]'

    def citations_for(self, source_id: str) -> List[Citation]:
        """All citations attributed to *source_id*."""
        return [c for c in self._citations if c.source_id == source_id]

    def source(self, source_id: str) -> Optional[Source]:
        """Fetch a registered source, or None."""
        return self._sources.get(source_id)

    def __len__(self) -> int:
        return len(self._citations)
'''

FILES["Backend/knowledge/provenance/evidence.py"] = '''"""Evidence ledger: which sources support which claims."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from knowledge.provenance.source import Source

__all__ = ["Evidence", "EvidenceLedger"]


@dataclass
class Evidence:
    """A claim plus the sources that support it."""

    claim: str
    source_ids: List[str] = field(default_factory=list)


class EvidenceLedger:
    """Tracks claims and their supporting sources with trust aggregation."""

    def __init__(self) -> None:
        self._evidence: Dict[str, Evidence] = {}
        self._sources: Dict[str, Source] = {}

    def register_source(self, source: Source) -> None:
        """Register a source for trust lookups."""
        self._sources[source.source_id] = source

    def add_evidence(self, claim: str, source_ids: List[str]) -> Evidence:
        """Record evidence for *claim*; unknown sources raise KeyError."""
        for sid in source_ids:
            if sid not in self._sources:
                raise KeyError(f"unknown source: {sid!r}")
        evidence = self._evidence.get(claim)
        if evidence is None:
            evidence = Evidence(claim=claim)
            self._evidence[claim] = evidence
        for sid in source_ids:
            if sid not in evidence.source_ids:
                evidence.source_ids.append(sid)
        return evidence

    def support_score(self, claim: str) -> float:
        """Mean trust of supporting sources; 0.0 when unsupported."""
        evidence = self._evidence.get(claim)
        if not evidence or not evidence.source_ids:
            return 0.0
        total = sum(
            self._sources[sid].trust for sid in evidence.source_ids
        )
        return total / len(evidence.source_ids)

    def is_supported(self, claim: str, min_trust: float = 0.5) -> bool:
        """True when support_score meets *min_trust*."""
        return self.support_score(claim) >= min_trust

    def evidence_for(self, claim: str) -> Optional[Evidence]:
        """Evidence record for *claim*, or None."""
        return self._evidence.get(claim)

    def __len__(self) -> int:
        return len(self._evidence)
'''

FILES["Backend/knowledge/provenance/lineage.py"] = '''"""Lineage tracking: transformation history of derived knowledge."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

__all__ = ["LineageTracker", "Transformation"]


@dataclass(frozen=True)
class Transformation:
    """One derivation step: inputs consumed, output produced."""

    output_id: str
    input_ids: tuple
    operation: str
    metadata: Dict[str, str] = field(default_factory=dict)


class LineageTracker:
    """Records how artifacts were derived and traces origins."""

    def __init__(self) -> None:
        self._steps: Dict[str, List[Transformation]] = {}

    def record(
        self,
        output_id: str,
        input_ids: List[str],
        operation: str,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Transformation:
        """Record that *output_id* was produced from *input_ids*."""
        step = Transformation(
            output_id=output_id,
            input_ids=tuple(input_ids),
            operation=operation,
            metadata=dict(metadata or {}),
        )
        self._steps.setdefault(output_id, []).append(step)
        return step

    def direct_inputs(self, artifact_id: str) -> List[str]:
        """Inputs of the most recent transformation of *artifact_id*."""
        steps = self._steps.get(artifact_id)
        return list(steps[-1].input_ids) if steps else []

    def origins(self, artifact_id: str, max_depth: int = 32) -> List[str]:
        """Root artifacts with no recorded transformation (BFS, bounded).

        Deterministic: inputs are visited in recorded order.
        """
        if max_depth < 1:
            raise ValueError("max_depth must be >= 1")
        roots: List[str] = []
        frontier = [artifact_id]
        depth = 0
        while frontier and depth < max_depth:
            nxt: List[str] = []
            for node in frontier:
                steps = self._steps.get(node)
                if not steps:
                    if node not in roots:
                        roots.append(node)
                    continue
                nxt.extend(steps[-1].input_ids)
            frontier = nxt
            depth += 1
        return roots

    def history(self, artifact_id: str) -> List[Transformation]:
        """All recorded transformations of *artifact_id* in order."""
        return list(self._steps.get(artifact_id, []))
'''

# ---------------------------------------------------------------- Backend/learning/__init__
FILES["Backend/learning/__init__.py"] = '''"""Learning layer: training, feedback, continual learning, adaptation."""
'''

FILES["Backend/learning/Research/training/__init__.py"] = '''"""Training subsystem: datasets, features, evaluation, checkpoints."""
'''

FILES["Backend/learning/feedback/__init__.py"] = '''"""Feedback subsystem: reward signals and correction learning."""
'''

FILES["Backend/learning/continual/__init__.py"] = '''"""Continual learning subsystem: drift, forgetting, consolidation."""
'''

FILES["Backend/learning/adaptation/__init__.py"] = '''"""Adaptation subsystem: policy and parameter adaptation."""
'''

# ---------------------------------------------------------------- Backend/learning/training
FILES["Backend/learning/Research/training/dataset_builder.py"] = '''"""Deterministic dataset construction and splitting."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Sequence, Tuple

__all__ = ["DatasetBuilder", "Example"]


@dataclass(frozen=True)
class Example:
    """A labeled training example."""

    text: str
    label: str


class DatasetBuilder:
    """Collects examples and produces deterministic train/val splits."""

    def __init__(self, seed: int = 0) -> None:
        self._examples: List[Example] = []
        self._seed = seed

    def add(self, text: str, label: str) -> Example:
        """Add a labeled example."""
        example = Example(text=text, label=label)
        self._examples.append(example)
        return example

    def __len__(self) -> int:
        return len(self._examples)

    def examples(self) -> List[Example]:
        """All examples in insertion order."""
        return list(self._examples)

    def labels(self) -> List[str]:
        """Distinct labels in first-seen order."""
        seen: List[str] = []
        for ex in self._examples:
            if ex.label not in seen:
                seen.append(ex.label)
        return seen

    def split(
        self, validation_ratio: float = 0.2
    ) -> Tuple[List[Example], List[Example]]:
        """Shuffled (seeded) train/validation split.

        The shuffle uses a local Random(self._seed) so repeated calls with
        the same data return identical splits regardless of global state.
        """
        if not 0.0 <= validation_ratio < 1.0:
            raise ValueError("validation_ratio must be within [0, 1)")
        examples = list(self._examples)
        rng = random.Random(self._seed)
        rng.shuffle(examples)
        n_val = int(len(examples) * validation_ratio)
        return examples[n_val:], examples[:n_val]
'''

FILES["Backend/learning/Research/training/feature_builder.py"] = '''"""Feature building: fixed-vocabulary bag-of-words vectors."""

from __future__ import annotations

import re
from typing import Dict, List, Sequence, Tuple

__all__ = ["FeatureBuilder"]

_TOKEN_RE = re.compile(r"[a-z0-9]+")


class FeatureBuilder:
    """Builds sparse bag-of-words features from a fixed vocabulary.

    The vocabulary is learned from ``fit`` (insertion order) and frozen
    thereafter; unseen tokens at transform time are ignored.
    """

    def __init__(self, max_features: int = 512) -> None:
        if max_features < 1:
            raise ValueError("max_features must be >= 1")
        self._max_features = max_features
        self._vocab: Dict[str, int] = {}

    @property
    def vocabulary(self) -> List[str]:
        """Feature tokens in index order."""
        return list(self._vocab)

    def fit(self, texts: Sequence[str]) -> "FeatureBuilder":
        """Learn the vocabulary from *texts* (most frequent first)."""
        counts: Dict[str, int] = {}
        for text in texts:
            for token in _TOKEN_RE.findall(text.lower()):
                counts[token] = counts.get(token, 0) + 1
        ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
        self._vocab = {
            token: idx
            for idx, (token, _) in enumerate(ranked[: self._max_features])
        }
        return self

    def transform(self, text: str) -> List[Tuple[int, float]]:
        """Sparse (index, count) features for *text*."""
        counts: Dict[int, float] = {}
        for token in _TOKEN_RE.findall(text.lower()):
            idx = self._vocab.get(token)
            if idx is not None:
                counts[idx] = counts.get(idx, 0.0) + 1.0
        return sorted(counts.items())

    def fit_transform(self, texts: Sequence[str]) -> List[List[Tuple[int, float]]]:
        """Fit on *texts* then transform each one."""
        self.fit(texts)
        return [self.transform(t) for t in texts]
'''

FILES["Backend/learning/Research/training/evaluator.py"] = '''"""Classification metrics: accuracy, precision, recall, F1."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence

__all__ = ["Evaluator", "Metrics"]


@dataclass(frozen=True)
class Metrics:
    """Evaluation metrics for one label or the macro average."""

    accuracy: float
    precision: float
    recall: float
    f1: float
    support: int


class Evaluator:
    """Computes deterministic classification metrics."""

    @staticmethod
    def accuracy(truth: Sequence[str], pred: Sequence[str]) -> float:
        """Fraction of matching labels (0.0 for empty input)."""
        if len(truth) != len(pred):
            raise ValueError("truth and pred must have equal length")
        if not truth:
            return 0.0
        return sum(t == p for t, p in zip(truth, pred)) / len(truth)

    @staticmethod
    def per_label(truth: Sequence[str], pred: Sequence[str]) -> Dict[str, Metrics]:
        """Precision/recall/F1 per distinct label plus overall accuracy."""
        if len(truth) != len(pred):
            raise ValueError("truth and pred must have equal length")
        labels: List[str] = []
        for label in list(truth) + list(pred):
            if label not in labels:
                labels.append(label)
        overall_acc = Evaluator.accuracy(truth, pred)
        result: Dict[str, Metrics] = {}
        for label in labels:
            tp = sum(
                1 for t, p in zip(truth, pred) if t == label and p == label
            )
            fp = sum(
                1 for t, p in zip(truth, pred) if t != label and p == label
            )
            fn = sum(
                1 for t, p in zip(truth, pred) if t == label and p != label
            )
            support = sum(1 for t in truth if t == label)
            precision = tp / (tp + fp) if (tp + fp) else 0.0
            recall = tp / (tp + fn) if (tp + fn) else 0.0
            f1 = (
                2 * precision * recall / (precision + recall)
                if (precision + recall)
                else 0.0
            )
            result[label] = Metrics(
                accuracy=overall_acc,
                precision=precision,
                recall=recall,
                f1=f1,
                support=support,
            )
        return result

    @staticmethod
    def macro_f1(truth: Sequence[str], pred: Sequence[str]) -> float:
        """Unweighted mean of per-label F1 (0.0 for empty input)."""
        per = Evaluator.per_label(truth, pred)
        if not per:
            return 0.0
        return sum(m.f1 for m in per.values()) / len(per)
'''

FILES["Backend/learning/Research/training/checkpoints.py"] = '''"""Training checkpoints persisted as JSON via an injected store."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

__all__ = ["CheckpointStore"]

Writer = Callable[[str, str], None]
Loader = Callable[[str], str]


class CheckpointStore:
    """Named, versioned checkpoints with pluggable persistence.

    The default backend writes JSON files under a directory; tests can
    inject in-memory ``writer``/``loader`` callables instead.
    """

    def __init__(
        self,
        directory: Optional[Path] = None,
        writer: Optional[Writer] = None,
        loader: Optional[Loader] = None,
    ) -> None:
        if directory is None and (writer is None or loader is None):
            raise ValueError(
                "provide a directory or both writer and loader callables"
            )
        self._directory = Path(directory) if directory else None
        self._writer = writer
        self._loader = loader

    def _key(self, name: str, version: int) -> str:
        return f"{name}.v{version}.json"

    def save(self, name: str, state: Dict[str, Any], version: int = 1) -> str:
        """Persist *state* under *name*/*version*; returns the storage key."""
        if version < 1:
            raise ValueError("version must be >= 1")
        payload = json.dumps(
            {"name": name, "version": version, "state": state},
            sort_keys=True,
        )
        key = self._key(name, version)
        if self._writer is not None:
            self._writer(key, payload)
        else:
            assert self._directory is not None
            self._directory.mkdir(parents=True, exist_ok=True)
            (self._directory / key).write_text(payload, encoding="utf-8")
        return key

    def load(self, name: str, version: int = 1) -> Dict[str, Any]:
        """Load checkpoint state; raises FileNotFoundError when missing."""
        key = self._key(name, version)
        if self._loader is not None:
            raw = self._loader(key)
        else:
            assert self._directory is not None
            path = self._directory / key
            if not path.is_file():
                raise FileNotFoundError(f"no checkpoint: {key}")
            raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
        return data["state"]

    def exists(self, name: str, version: int = 1) -> bool:
        """True when the checkpoint can be loaded."""
        try:
            self.load(name, version)
            return True
        except (FileNotFoundError, KeyError):
            return False

    def list_versions(self, name: str) -> List[int]:
        """Versions present for *name*, ascending (directory backend only)."""
        if self._directory is None:
            return []
        prefix = f"{name}.v"
        suffix = ".json"
        versions: List[int] = []
        if self._directory.is_dir():
            for path in self._directory.iterdir():
                fname = path.name
                if fname.startswith(prefix) and fname.endswith(suffix):
                    middle = fname[len(prefix):-len(suffix)]
                    if middle.isdigit():
                        versions.append(int(middle))
        return sorted(versions)
'''

# ---------------------------------------------------------------- Backend/learning/feedback
FILES["Backend/learning/feedback/reward_signals.py"] = '''"""Reward signal computation from ratings and outcomes."""

from __future__ import annotations

from typing import Dict, List, Sequence

__all__ = ["rating_to_reward", "discounted_rewards", "normalize_rewards"]

_RATING_MAP: Dict[str, float] = {
    "thumbs_up": 1.0,
    "thumbs_down": -1.0,
    "positive": 1.0,
    "negative": -1.0,
    "neutral": 0.0,
}


def rating_to_reward(rating: str) -> float:
    """Map a symbolic rating to a reward in [-1, 1].

    Numeric strings in [0, 1] map linearly to [-1, 1]; unknown symbols
    raise ValueError.
    """
    if rating in _RATING_MAP:
        return _RATING_MAP[rating]
    try:
        value = float(rating)
    except ValueError:
        raise ValueError(f"unknown rating: {rating!r}") from None
    if not 0.0 <= value <= 1.0:
        raise ValueError("numeric ratings must be within [0, 1]")
    return value * 2.0 - 1.0


def discounted_rewards(
    rewards: Sequence[float], gamma: float = 0.9
) -> List[float]:
    """Return-to-go with discount *gamma* (higher weight to earlier steps)."""
    if not 0.0 <= gamma <= 1.0:
        raise ValueError("gamma must be within [0, 1]")
    result = [0.0] * len(rewards)
    running = 0.0
    for i in range(len(rewards) - 1, -1, -1):
        running = rewards[i] + gamma * running
        result[i] = running
    return result


def normalize_rewards(rewards: Sequence[float]) -> List[float]:
    """Min-max scale rewards to [0, 1]; all-equal input maps to 0.5."""
    if not rewards:
        return []
    lo, hi = min(rewards), max(rewards)
    if hi == lo:
        return [0.5] * len(rewards)
    span = hi - lo
    return [(r - lo) / span for r in rewards]
'''

FILES["Backend/learning/feedback/correction_learning.py"] = '''"""Learning from user corrections with normalized-input lookup."""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple

__all__ = ["CorrectionLearner"]

_WS_RE = re.compile(r"\\s+")


class CorrectionLearner:
    """Stores (input, wrong_output, corrected_output) triples.

    Suggestions are looked up by whitespace-normalized input so minor
    formatting differences still match. Deterministic: the most frequent
    correction wins, ties break by insertion order.
    """

    def __init__(self) -> None:
        self._corrections: Dict[str, List[Tuple[str, str]]] = {}

    @staticmethod
    def _normalize(text: str) -> str:
        return _WS_RE.sub(" ", text.strip().lower())

    def record(
        self, input_text: str, wrong_output: str, corrected_output: str
    ) -> bool:
        """Record a correction; returns False when it is a no-op."""
        if wrong_output == corrected_output:
            return False
        key = self._normalize(input_text)
        self._corrections.setdefault(key, []).append(
            (wrong_output, corrected_output)
        )
        return True

    def suggest(self, input_text: str) -> Optional[str]:
        """Most-recorded corrected output for this input, or None."""
        entries = self._corrections.get(self._normalize(input_text))
        if not entries:
            return None
        counts: Dict[str, int] = {}
        for _, corrected in entries:
            counts[corrected] = counts.get(corrected, 0) + 1
        best = max(counts.items(), key=lambda kv: (kv[1], -entries.index(
            next(e for e in entries if e[1] == kv[0])
        )))
        return best[0]

    def known_inputs(self) -> List[str]:
        """Normalized inputs with at least one correction, sorted."""
        return sorted(self._corrections)

    def __len__(self) -> int:
        return len(self._corrections)
'''

# ---------------------------------------------------------------- Backend/learning/continual
FILES["Backend/learning/continual/concept_drift.py"] = '''"""Concept drift detection over a rolling accuracy window."""

from __future__ import annotations

from collections import deque
from typing import Deque, List, Optional

__all__ = ["DriftDetector"]


class DriftDetector:
    """Flags drift when recent performance drops below a baseline margin.

    A long window tracks the stable baseline; a short window tracks
    recent behavior. Drift is signaled when the recent mean falls below
    ``baseline_mean - threshold``.
    """

    def __init__(
        self,
        window_size: int = 50,
        recent_size: int = 10,
        threshold: float = 0.1,
    ) -> None:
        if window_size < 2 or recent_size < 1:
            raise ValueError("window_size >= 2 and recent_size >= 1 required")
        if recent_size > window_size:
            raise ValueError("recent_size must not exceed window_size")
        if threshold < 0.0:
            raise ValueError("threshold must be >= 0")
        self._baseline: Deque[float] = deque(maxlen=window_size)
        self._recent: Deque[float] = deque(maxlen=recent_size)
        self._threshold = threshold

    def observe(self, value: float) -> bool:
        """Record a performance value; returns True when drift is detected."""
        self._baseline.append(value)
        self._recent.append(value)
        if len(self._recent) < self._recent.maxlen:
            return False
        if len(self._baseline) < 2:
            return False
        baseline_mean = sum(self._baseline) / len(self._baseline)
        recent_mean = sum(self._recent) / len(self._recent)
        return recent_mean < baseline_mean - self._threshold

    def baseline_mean(self) -> Optional[float]:
        """Mean of the baseline window, or None when empty."""
        if not self._baseline:
            return None
        return sum(self._baseline) / len(self._baseline)

    def recent_mean(self) -> Optional[float]:
        """Mean of the recent window, or None when empty."""
        if not self._recent:
            return None
        return sum(self._recent) / len(self._recent)

    def reset(self) -> None:
        """Clear both windows."""
        self._baseline.clear()
        self._recent.clear()

    def history(self) -> List[float]:
        """Baseline window contents (oldest first)."""
        return list(self._baseline)
'''

FILES["Backend/learning/continual/forgetting_detector.py"] = '''"""Catastrophic forgetting detection from accuracy snapshots."""

from __future__ import annotations

from typing import Dict, List, Optional

__all__ = ["ForgettingDetector"]


class ForgettingDetector:
    """Compares per-task accuracy snapshots to detect regressions.

    Snapshots are recorded per task; ``forgetting`` is the drop from the
    best historical accuracy to the current one.
    """

    def __init__(self, threshold: float = 0.05) -> None:
        if threshold < 0.0:
            raise ValueError("threshold must be >= 0")
        self._threshold = threshold
        self._best: Dict[str, float] = {}
        self._current: Dict[str, float] = {}

    def record(self, task: str, accuracy: float) -> bool:
        """Record an accuracy for *task*; returns True when forgetting.

        Forgetting is signaled when the drop from the best recorded
        accuracy exceeds the threshold.
        """
        if not 0.0 <= accuracy <= 1.0:
            raise ValueError("accuracy must be within [0, 1]")
        self._current[task] = accuracy
        best = self._best.get(task)
        if best is None or accuracy > best:
            self._best[task] = accuracy
            return False
        return (best - accuracy) > self._threshold

    def forgetting(self, task: str) -> Optional[float]:
        """Current forgetting amount for *task* (best - current), or None."""
        if task not in self._best or task not in self._current:
            return None
        return self._best[task] - self._current[task]

    def is_forgetting(self, task: str) -> bool:
        """True when forgetting exceeds the threshold."""
        amount = self.forgetting(task)
        return amount is not None and amount > self._threshold

    def tasks(self) -> List[str]:
        """Tracked tasks in first-recorded order."""
        seen: List[str] = []
        for task in list(self._best) + list(self._current):
            if task not in seen:
                seen.append(task)
        return seen
'''

FILES["Backend/learning/continual/consolidation.py"] = '''"""Knowledge consolidation: merge new facts with importance weighting."""

from __future__ import annotations

from typing import Dict, List, Optional

__all__ = ["Consolidator"]


class Consolidator:
    """Merges incoming facts into a consolidated knowledge dict.

    Each fact carries an importance in [0, 1]. When a fact already exists,
    the higher importance wins and the value is overwritten; the winner
    count is tracked so callers can inspect merge behavior.
    """

    def __init__(self, decay: float = 0.0) -> None:
        if not 0.0 <= decay <= 1.0:
            raise ValueError("decay must be within [0, 1]")
        self._decay = decay
        self._facts: Dict[str, str] = {}
        self._importance: Dict[str, float] = {}
        self._updates: Dict[str, int] = {}

    def consolidate(
        self, key: str, value: str, importance: float = 0.5
    ) -> bool:
        """Merge one fact; returns True when the stored value changed."""
        if not 0.0 <= importance <= 1.0:
            raise ValueError("importance must be within [0, 1]")
        current_importance = self._importance.get(key)
        if current_importance is None or importance >= current_importance:
            changed = self._facts.get(key) != value
            self._facts[key] = value
            self._importance[key] = max(importance, current_importance or 0.0)
            self._updates[key] = self._updates.get(key, 0) + 1
            return changed
        return False

    def get(self, key: str) -> Optional[str]:
        """Consolidated value for *key*, or None."""
        return self._facts.get(key)

    def importance(self, key: str) -> Optional[float]:
        """Stored importance for *key*, or None."""
        return self._importance.get(key)

    def forget(self, key: str) -> bool:
        """Drop a fact; returns True when something was removed."""
        if key not in self._facts:
            return False
        del self._facts[key]
        self._importance.pop(key, None)
        self._updates.pop(key, None)
        return True

    def keys(self) -> List[str]:
        """Consolidated keys in insertion order."""
        return list(self._facts)

    def __len__(self) -> int:
        return len(self._facts)
'''

# ---------------------------------------------------------------- Backend/learning/adaptation
FILES["Backend/learning/adaptation/policy_adaptation.py"] = '''"""Policy adaptation: exponential-moving-average parameter updates."""

from __future__ import annotations

from typing import Dict, List, Optional

__all__ = ["PolicyAdapter"]


class PolicyAdapter:
    """Adapts named policy parameters from scalar feedback via EMA.

    ``update(name, feedback)`` moves the parameter toward the feedback
    value with learning rate ``alpha``; parameters are clamped to
    ``[min_value, max_value]``.
    """

    def __init__(
        self,
        alpha: float = 0.2,
        min_value: float = 0.0,
        max_value: float = 1.0,
    ) -> None:
        if not 0.0 < alpha <= 1.0:
            raise ValueError("alpha must be within (0, 1]")
        if min_value >= max_value:
            raise ValueError("min_value must be < max_value")
        self._alpha = alpha
        self._min = min_value
        self._max = max_value
        self._params: Dict[str, float] = {}
        self._history: Dict[str, List[float]] = {}

    def set_initial(self, name: str, value: float) -> None:
        """Seed a parameter (clamped); overwrites any current value."""
        self._params[name] = self._clamp(value)

    def get(self, name: str) -> Optional[float]:
        """Current parameter value, or None when unset."""
        return self._params.get(name)

    def update(self, name: str, feedback: float) -> float:
        """EMA update toward *feedback*; returns the new value."""
        target = self._clamp(feedback)
        current = self._params.get(name)
        if current is None:
            new_value = target
        else:
            new_value = current + self._alpha * (target - current)
        new_value = self._clamp(new_value)
        self._params[name] = new_value
        self._history.setdefault(name, []).append(new_value)
        return new_value

    def history(self, name: str) -> List[float]:
        """Value history for *name* after each update."""
        return list(self._history.get(name, []))

    def parameters(self) -> Dict[str, float]:
        """Snapshot of all parameters."""
        return dict(self._params)

    def _clamp(self, value: float) -> float:
        return max(self._min, min(self._max, value))
'''

# ---------------------------------------------------------------- Backend/models/liquid
FILES["Backend/models/liquid/__init__.py"] = '''"""Liquid time-constant networks: cells, dynamics, checkpoints."""
'''

FILES["Backend/models/liquid/lnn/__init__.py"] = '''"""LNN core: architecture, cells, dynamics, intent model, optimizer."""
'''

FILES["Backend/models/liquid/checkpoints/__init__.py"] = '''"""Checkpoint management and validation for liquid models."""
'''

FILES["Backend/models/liquid/lnn/cells.py"] = '''"""Liquid cell: deterministic leaky-integrator time-constant unit."""

from __future__ import annotations

import math
from typing import List, Sequence

__all__ = ["LiquidCell"]


class LiquidCell:
    """Single-input liquid time-constant cell.

    Discrete-time update (Euler integration of a first-order ODE):

        h[t+1] = (1 - dt/tau) * h[t] + (dt/tau) * tanh(w * x[t] + b)

    All arithmetic is plain Python floats, so results are deterministic
    across platforms and require no ML framework.
    """

    def __init__(
        self,
        weight: float = 1.0,
        bias: float = 0.0,
        tau: float = 1.0,
        dt: float = 0.1,
    ) -> None:
        if tau <= 0.0:
            raise ValueError("tau must be > 0")
        if dt <= 0.0:
            raise ValueError("dt must be > 0")
        if dt > tau:
            raise ValueError("dt must not exceed tau (stability)")
        self.weight = weight
        self.bias = bias
        self.tau = tau
        self.dt = dt
        self.state = 0.0

    @property
    def decay(self) -> float:
        """Per-step retention factor ``1 - dt/tau``."""
        return 1.0 - self.dt / self.tau

    def reset(self) -> None:
        """Zero the hidden state."""
        self.state = 0.0

    def step(self, x: float) -> float:
        """Advance one timestep with input *x*; returns the new state."""
        drive = math.tanh(self.weight * x + self.bias)
        self.state = self.decay * self.state + (self.dt / self.tau) * drive
        return self.state

    def run(self, inputs: Sequence[float]) -> List[float]:
        """Run over an input sequence, returning all states."""
        self.reset()
        return [self.step(x) for x in inputs]
'''

FILES["Backend/models/liquid/lnn/dynamics.py"] = '''"""Dynamics helpers: simulation and time-constant sweeps."""

from __future__ import annotations

from typing import Callable, List, Sequence, Tuple

from models.liquid.lnn.cells import LiquidCell

__all__ = ["simulate", "sweep_tau", "steady_state"]


def simulate(cell: LiquidCell, inputs: Sequence[float]) -> List[float]:
    """Run *cell* over *inputs* and return the state trajectory."""
    return cell.run(inputs)


def sweep_tau(
    taus: Sequence[float],
    inputs: Sequence[float],
    weight: float = 1.0,
    bias: float = 0.0,
    dt: float = 0.1,
) -> List[Tuple[float, float]]:
    """Final state for each candidate tau (deterministic order).

    Returns (tau, final_state) pairs; useful for picking a time constant
    that settles quickly or retains memory, depending on the task.
    """
    results: List[Tuple[float, float]] = []
    for tau in taus:
        cell = LiquidCell(weight=weight, bias=bias, tau=tau, dt=dt)
        trajectory = cell.run(inputs)
        results.append((tau, trajectory[-1] if trajectory else 0.0))
    return results


def steady_state(cell: LiquidCell, x: float, steps: int = 200) -> float:
    """Drive the cell with constant input until it settles.

    Returns the state after *steps* iterations; with dt <= tau the update
    is a contraction, so this converges to the fixed point.
    """
    if steps < 1:
        raise ValueError("steps must be >= 1")
    cell.reset()
    state = 0.0
    for _ in range(steps):
        state = cell.step(x)
    return state
'''

FILES["Backend/models/liquid/lnn/architecture.py"] = '''"""Liquid network: a chain of cells with per-layer time constants."""

from __future__ import annotations

from typing import Any, Dict, List, Sequence

from models.liquid.lnn.cells import LiquidCell

__all__ = ["LiquidNetwork"]


class LiquidNetwork:
    """Feedforward-in-time stack of liquid cells.

    Layer i receives the state of layer i-1 as its input; the first layer
    receives the external input. States are exposed for inspection and
    checkpointing.
    """

    def __init__(
        self,
        layer_taus: Sequence[float],
        weight: float = 1.0,
        bias: float = 0.0,
        dt: float = 0.1,
    ) -> None:
        if not layer_taus:
            raise ValueError("at least one layer is required")
        self.cells: List[LiquidCell] = [
            LiquidCell(weight=weight, bias=bias, tau=tau, dt=dt)
            for tau in layer_taus
        ]

    @property
    def num_layers(self) -> int:
        """Number of stacked cells."""
        return len(self.cells)

    def reset(self) -> None:
        """Reset every cell."""
        for cell in self.cells:
            cell.reset()

    def step(self, x: float) -> List[float]:
        """Advance one timestep; returns per-layer states."""
        states: List[float] = []
        signal = x
        for cell in self.cells:
            signal = cell.step(signal)
            states.append(signal)
        return states

    def forward(self, inputs: Sequence[float]) -> List[List[float]]:
        """Run a sequence; returns one state list per timestep."""
        self.reset()
        return [self.step(x) for x in inputs]

    def state_dict(self) -> Dict[str, Any]:
        """Serializable parameters and current state."""
        return {
            "taus": [c.tau for c in self.cells],
            "weights": [c.weight for c in self.cells],
            "biases": [c.bias for c in self.cells],
            "dt": self.cells[0].dt,
            "state": [c.state for c in self.cells],
        }

    def load_state_dict(self, state: Dict[str, Any]) -> None:
        """Restore parameters and state produced by ``state_dict``."""
        taus = state["taus"]
        if len(taus) != len(self.cells):
            raise ValueError("layer count mismatch")
        for cell, tau, weight, bias, cell_state in zip(
            self.cells, taus, state["weights"], state["biases"], state["state"]
        ):
            cell.tau = tau
            cell.weight = weight
            cell.bias = bias
            cell.state = cell_state
'''

FILES["Backend/models/liquid/lnn/intent_model.py"] = '''"""Intent model: liquid encoder + nearest-prototype classifier head."""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

from models.liquid.lnn.architecture import LiquidNetwork

__all__ = ["LiquidIntentModel"]


class LiquidIntentModel:
    """Deterministic intent classifier over liquid dynamics.

    Text is encoded to a scalar signal (mean character code, normalized),
    pushed through a liquid network, and the final hidden state is matched
    against per-intent prototypes learned from labeled examples. No ML
    framework or network access is involved.
    """

    def __init__(self, layer_taus: Sequence[float] = (1.0, 2.0)) -> None:
        self.network = LiquidNetwork(layer_taus)
        self._prototypes: Dict[str, List[float]] = {}
        self._examples: Dict[str, List[float]] = {}

    @staticmethod
    def encode(text: str) -> float:
        """Deterministic scalar encoding of text into [-1, 1]."""
        if not text:
            return 0.0
        codes = [ord(ch) for ch in text]
        mean_code = sum(codes) / len(codes)
        return (mean_code - 96.0) / 32.0  # ~[-1, 1] for lowercase text

    def add_example(self, text: str, intent: str) -> None:
        """Record a labeled example for prototype estimation."""
        self.network.reset()
        states = self.network.forward([self.encode(text)])
        final = states[-1][-1] if states and states[-1] else 0.0
        self._examples.setdefault(intent, []).append(final)

    def fit(self) -> None:
        """(Re)compute per-intent prototype means from examples."""
        self._prototypes = {
            intent: [sum(vals) / len(vals)]
            for intent, vals in self._examples.items()
        }

    def predict(self, text: str) -> Tuple[Optional[str], float]:
        """Predict (intent, confidence); (None, 0.0) when unfitted."""
        if not self._prototypes:
            return None, 0.0
        self.network.reset()
        states = self.network.forward([self.encode(text)])
        final = states[-1][-1] if states and states[-1] else 0.0
        best_intent: Optional[str] = None
        best_distance = float("inf")
        for intent, proto in self._prototypes.items():
            distance = abs(final - proto[0])
            if distance < best_distance:
                best_distance = distance
                best_intent = intent
        confidence = 1.0 / (1.0 + best_distance)
        return best_intent, confidence

    def num_intents(self) -> int:
        """Number of fitted intents."""
        return len(self._prototypes)
'''

FILES["Backend/models/liquid/lnn/optimizer.py"] = '''"""Gradient-free optimizer: seeded hill climbing over parameters."""

from __future__ import annotations

import random
from typing import Callable, Dict, List, Tuple

__all__ = ["HillClimbOptimizer"]

Objective = Callable[[Dict[str, float]], float]


class HillClimbOptimizer:
    """Deterministic random-restart-free hill climbing.

    Uses a local ``random.Random(seed)`` so runs are reproducible without
    touching global RNG state. The objective is maximized.
    """

    def __init__(
        self,
        param_bounds: Dict[str, Tuple[float, float]],
        step_size: float = 0.1,
        seed: int = 0,
    ) -> None:
        if not param_bounds:
            raise ValueError("at least one parameter is required")
        if step_size <= 0.0:
            raise ValueError("step_size must be > 0")
        for name, (lo, hi) in param_bounds.items():
            if lo >= hi:
                raise ValueError(f"invalid bounds for {name!r}: {lo} >= {hi}")
        self._bounds = dict(param_bounds)
        self._step = step_size
        self._rng = random.Random(seed)

    def optimize(
        self,
        objective: Objective,
        iterations: int = 100,
        initial: Dict[str, float] | None = None,
    ) -> Tuple[Dict[str, float], float]:
        """Maximize *objective*; returns (best_params, best_score)."""
        if iterations < 1:
            raise ValueError("iterations must be >= 1")
        if initial is None:
            current = {
                name: self._rng.uniform(lo, hi)
                for name, (lo, hi) in self._bounds.items()
            }
        else:
            current = {
                name: self._clamp(name, initial.get(name, (lo + hi) / 2.0))
                for name, (lo, hi) in self._bounds.items()
            }
        best_params = dict(current)
        best_score = objective(current)
        for _ in range(iterations):
            candidate = {
                name: self._clamp(
                    name, value + self._rng.uniform(-self._step, self._step)
                )
                for name, value in current.items()
            }
            score = objective(candidate)
            if score > best_score:
                best_score = score
                best_params = dict(candidate)
                current = candidate
        return best_params, best_score

    def _clamp(self, name: str, value: float) -> float:
        lo, hi = self._bounds[name]
        return max(lo, min(hi, value))

    def history_note(self) -> str:
        """Human-readable description of the search configuration."""
        names = ", ".join(sorted(self._bounds))
        return f"hill climbing over [{names}] with step {self._step}"
'''

FILES["Backend/models/liquid/checkpoints/manager.py"] = '''"""Checkpoint manager for liquid models (JSON, injected persistence)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

__all__ = ["CheckpointManager"]

Writer = Callable[[str, str], None]
Loader = Callable[[str], str]


class CheckpointManager:
    """Saves/loads model state dicts with format-version metadata.

    Persistence is pluggable: pass a directory (file backend) or
    writer/loader callables (in-memory backend for tests).
    """

    FORMAT_VERSION = 1

    def __init__(
        self,
        directory: Optional[Path] = None,
        writer: Optional[Writer] = None,
        loader: Optional[Loader] = None,
    ) -> None:
        if directory is None and (writer is None or loader is None):
            raise ValueError(
                "provide a directory or both writer and loader callables"
            )
        self._directory = Path(directory) if directory else None
        self._writer = writer
        self._loader = loader

    def _key(self, name: str) -> str:
        return f"{name}.liquid.json"

    def save(self, name: str, state: Dict[str, Any]) -> str:
        """Persist *state* under *name*; returns the storage key."""
        payload = json.dumps(
            {
                "format_version": self.FORMAT_VERSION,
                "name": name,
                "state": state,
            },
            sort_keys=True,
        )
        key = self._key(name)
        if self._writer is not None:
            self._writer(key, payload)
        else:
            assert self._directory is not None
            self._directory.mkdir(parents=True, exist_ok=True)
            (self._directory / key).write_text(payload, encoding="utf-8")
        return key

    def load(self, name: str) -> Dict[str, Any]:
        """Load state; raises FileNotFoundError when absent."""
        key = self._key(name)
        if self._loader is not None:
            raw = self._loader(key)
        else:
            assert self._directory is not None
            path = self._directory / key
            if not path.is_file():
                raise FileNotFoundError(f"no checkpoint: {key}")
            raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
        version = data.get("format_version")
        if version != self.FORMAT_VERSION:
            raise ValueError(f"unsupported checkpoint format: {version!r}")
        return data["state"]

    def exists(self, name: str) -> bool:
        """True when the checkpoint loads cleanly."""
        try:
            self.load(name)
            return True
        except (FileNotFoundError, ValueError, KeyError):
            return False

    def list_checkpoints(self) -> List[str]:
        """Checkpoint names present (directory backend only)."""
        if self._directory is None or not self._directory.is_dir():
            return []
        names: List[str] = []
        for path in sorted(self._directory.iterdir()):
            if path.name.endswith(".liquid.json"):
                names.append(path.name[: -len(".liquid.json")])
        return names
'''

FILES["Backend/models/liquid/checkpoints/validator.py"] = '''"""Checkpoint validation for liquid model state dicts."""

from __future__ import annotations

from typing import Any, Dict, List, Sequence

__all__ = ["validate_checkpoint", "ValidationError"]

REQUIRED_KEYS = ("taus", "weights", "biases", "dt", "state")


class ValidationError(ValueError):
    """Raised when a checkpoint fails structural validation."""


def validate_checkpoint(
    state: Dict[str, Any],
    required_keys: Sequence[str] = REQUIRED_KEYS,
) -> List[str]:
    """Validate a liquid state dict; returns a list of problems (empty=OK).

    Checks performed:
      * all required keys present
      * taus/weights/biases are equal-length lists of finite floats
      * every tau > 0
      * state is a list of finite floats matching the layer count
    """
    problems: List[str] = []
    for key in required_keys:
        if key not in state:
            problems.append(f"missing key: {key}")
    if problems:
        return problems

    taus = state["taus"]
    weights = state["weights"]
    biases = state["biases"]
    cell_state = state["state"]
    dt = state["dt"]

    for name, seq in (
        ("taus", taus),
        ("weights", weights),
        ("biases", biases),
        ("state", cell_state),
    ):
        if not isinstance(seq, list):
            problems.append(f"{name} must be a list")
            return problems
        if len(seq) != len(taus):
            problems.append(f"{name} length {len(seq)} != taus length {len(taus)}")
            return problems
        for i, value in enumerate(seq):
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                problems.append(f"{name}[{i}] is not numeric")
                return problems
            if value != value or value in (float("inf"), float("-inf")):
                problems.append(f"{name}[{i}] is not finite")
                return problems

    for i, tau in enumerate(taus):
        if tau <= 0:
            problems.append(f"taus[{i}] must be > 0")
    if not isinstance(dt, (int, float)) or isinstance(dt, bool) or dt <= 0:
        problems.append("dt must be a positive number")
    elif dt > max(taus):
        problems.append("dt must not exceed the largest tau")
    return problems
'''


def main() -> None:
    for rel_path, content in FILES.items():
        path = pathlib.Path(rel_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
        print("wrote", rel_path)
    print(f"total: {len(FILES)} files")


if __name__ == "__main__":
    main()