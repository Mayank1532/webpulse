"""Deterministic evidence validation service."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from mcp_liveops.evidence.models import EvidenceRecord
from mcp_liveops.evidence.validation import (
    EvidenceValidationResult,
    ValidationReason,
)


class EvidenceValidator:
    """Validate EvidenceRecord instances without using an LLM."""

    def __init__(self, stale_after: timedelta = timedelta(days=30)) -> None:
        """Initialize validator with an explicit freshness threshold."""

        if stale_after <= timedelta(0):
            raise ValueError("stale_after must be greater than zero.")

        self._stale_after = stale_after

    def validate(
        self,
        evidence: EvidenceRecord,
        *,
        now: datetime | None = None,
    ) -> EvidenceValidationResult:
        """Validate evidence deterministically."""

        current_time = now or datetime.now(timezone.utc)

        if current_time.tzinfo is None:
            raise ValueError("now must be timezone-aware.")

        if evidence.retrieved_at > current_time:
            return EvidenceValidationResult(
                valid=False,
                reason=ValidationReason.FUTURE_RETRIEVAL_TIME,
                message="Evidence retrieval time cannot be in the future.",
            )

        if evidence.published_at is not None:
            if evidence.published_at > current_time:
                return EvidenceValidationResult(
                    valid=False,
                    reason=ValidationReason.FUTURE_PUBLICATION_TIME,
                    message="Publication time cannot be in the future.",
                )

            if evidence.published_at > evidence.retrieved_at:
                return EvidenceValidationResult(
                    valid=False,
                    reason=ValidationReason.PUBLICATION_AFTER_RETRIEVAL,
                    message="Publication time cannot be after retrieval time.",
                )

        age = current_time - evidence.retrieved_at

        if age > self._stale_after:
            return EvidenceValidationResult(
                valid=True,
                reason=ValidationReason.STALE,
                message="Evidence is structurally valid but stale.",
                stale=True,
            )

        return EvidenceValidationResult(
            valid=True,
            reason=ValidationReason.VALID,
            message="Evidence passed deterministic validation.",
        )

