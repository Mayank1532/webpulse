"""External API acquisition domain models."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class ExternalApiStatus(StrEnum):
    """Outcome of an external API acquisition operation."""

    SUCCESS = "success"
    EMPTY = "empty"
    FAILED = "failed"


class ExternalApiResponse(BaseModel):
    """Provider-neutral normalized external API response."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    provider: str = Field(min_length=1)
    endpoint: HttpUrl
    title: str = ""
    content: str = ""
    source_name: str = ""
    status: ExternalApiStatus
    message: str = Field(min_length=1)

