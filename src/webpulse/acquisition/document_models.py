"""Structured web document models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class WebDocument(BaseModel):
    """Clean, model-ready representation of a retrieved web page."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    url: HttpUrl
    title: str = ""
    text: str = Field(default="")
    content_type: str | None = None

    @property
    def usable(self) -> bool:
        """Return whether the document contains usable text."""
        return bool(self.text.strip())
