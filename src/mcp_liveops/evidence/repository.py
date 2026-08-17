"""Evidence repository abstractions."""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from mcp_liveops.evidence.models import EvidenceRecord


class EvidenceRepository(ABC):
    """Abstract repository for deterministic evidence storage."""

    @abstractmethod
    def add(self, evidence: EvidenceRecord) -> EvidenceRecord:
        """Store an evidence record."""
        raise NotImplementedError

    @abstractmethod
    def get(self, evidence_id: UUID) -> EvidenceRecord | None:
        """Return an evidence record by identifier."""
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> tuple[EvidenceRecord, ...]:
        """Return all stored evidence records."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, evidence_id: UUID) -> bool:
        """Delete an evidence record and report whether it existed."""
        raise NotImplementedError

    @abstractmethod
    def count(self) -> int:
        """Return the number of stored evidence records."""
        raise NotImplementedError

