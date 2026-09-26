"""Evidence ledger: which sources support which claims."""

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
