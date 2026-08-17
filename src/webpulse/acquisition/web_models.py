"""Web acquisition domain models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class WebSource(BaseModel):
    """Normalized representation of a web source."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    url: HttpUrl
    title: str = Field(min_length=1)
    content: str = Field(min_length=1)
    source_name: str = Field(min_length=1)


class WebAcquisitionResult(BaseModel):
    """Provider-neutral result returned by a web acquisition operation."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    url: HttpUrl
    title: str = ""
    content: str = ""
    source_name: str = ""
