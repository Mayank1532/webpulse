"""Evidence acquisition result models."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class AcquisitionStatus(StrEnum):
    """Outcome of an evidence acquisition operation."""

    SUCCESS = "success"
    EMPTY = "empty"
    FAILED = "failed"


class AcquisitionResult(BaseModel):
    """Result returned by an evidence acquisition adapter."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    status: AcquisitionStatus
    source_name: str = Field(min_length=1)
    content: str = ""
    source_uri: str | None = None
    retrieved_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    message: str = Field(min_length=1)

    @property
    def succeeded(self) -> bool:
        """Return whether acquisition produced usable content."""
        return self.status is AcquisitionStatus.SUCCESS

