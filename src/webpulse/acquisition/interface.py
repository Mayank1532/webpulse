"""Evidence acquisition interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod

from webpulse.acquisition.models import AcquisitionResult


class EvidenceAcquirer(ABC):
    """Abstract boundary for evidence acquisition sources."""

    @abstractmethod
    def acquire(self, source: str) -> AcquisitionResult:
        """Acquire evidence from a source identifier."""
        raise NotImplementedError
