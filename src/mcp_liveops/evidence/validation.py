"""Evidence validation result models."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class ValidationReason(StrEnum):
    """Deterministic reason for an evidence validation result."""

    VALID = "valid"
    BLANK_CLAIM = "blank_claim"
    BLANK_CONTENT = "blank_content"
    INVALID_CONFIDENCE = "invalid_confidence"
    INVALID_RELIABILITY = "invalid_reliability"
    FUTURE_RETRIEVAL_TIME = "future_retrieval_time"
    FUTURE_PUBLICATION_TIME = "future_publication_time"
    PUBLICATION_AFTER_RETRIEVAL = "publication_after_retrieval"
    STALE = "stale"


class EvidenceValidationResult(BaseModel):
    """Deterministic result produced by EvidenceValidator."""

    model_config = ConfigDict(frozen=True, extra='forbid')

    valid: bool
    reason: ValidationReason
    message: str
    stale: bool = False

