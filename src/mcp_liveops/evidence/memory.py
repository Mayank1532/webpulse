"""In-memory evidence repository implementation."""

from __future__ import annotations

from uuid import UUID

from mcp_liveops.evidence.models import EvidenceRecord
from mcp_liveops.evidence.repository import EvidenceRepository


class InMemoryEvidenceRepository(EvidenceRepository):
    """Deterministic in-memory repository for development and testing."""

    def __init__(self) -> None:
        """Initialize an empty evidence store."""
        self._records: dict[UUID, EvidenceRecord] = {}

    def add(self, evidence: EvidenceRecord) -> EvidenceRecord:
        """Store or replace an evidence record by its identifier."""
        self._records[evidence.evidence_id] = evidence
        return evidence

    def get(self, evidence_id: UUID) -> EvidenceRecord | None:
        """Retrieve evidence by identifier."""
        return self._records.get(evidence_id)

    def list_all(self) -> tuple[EvidenceRecord, ...]:
        """Return all evidence in insertion order."""
        return tuple(self._records.values())

    def delete(self, evidence_id: UUID) -> bool:
        """Delete evidence and report whether it existed."""
        if evidence_id not in self._records:
            return False

        del self._records[evidence_id]
        return True

    def count(self) -> int:
        """Return the number of stored records."""
        return len(self._records)

