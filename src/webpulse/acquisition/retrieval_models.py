"""Live web retrieval domain models."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class RetrievalStatus(StrEnum):
    """Outcome of a live web retrieval."""

    SUCCESS = "success"
    FAILED = "failed"


class WebRetrievalResult(BaseModel):
    """Structured result returned by the live HTTP retrieval layer."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    status: RetrievalStatus
    url: HttpUrl | None = None
    status_code: int | None = None
    content_type: str | None = None
    content: str = ""
    retrieved_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    message: str = Field(min_length=1)

    @property
    def succeeded(self) -> bool:
        """Return whether the retrieval succeeded."""
        return self.status is RetrievalStatus.SUCCESS
