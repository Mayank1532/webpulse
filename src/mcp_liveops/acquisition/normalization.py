"""Web source normalization service."""

from __future__ import annotations

import re

from mcp_liveops.acquisition.web_models import (
    WebAcquisitionResult,
    WebSource,
)


class WebSourceNormalizer:
    """Normalize provider-specific web results into stable source objects."""

    _WHITESPACE_PATTERN = re.compile(r"\s+")

    def normalize(self, result: WebAcquisitionResult) -> WebSource | None:
        """Normalize a web acquisition result.

        Returns None when the result does not contain usable evidence.
        """

        title = self._normalize_text(result.title)
        content = self._normalize_text(result.content)
        source_name = self._normalize_text(result.source_name)

        if not title or not content or not source_name:
            return None

        return WebSource(
            url=result.url,
            title=title,
            content=content,
            source_name=source_name,
        )

    def _normalize_text(self, value: str) -> str:
        """Normalize repeated whitespace and surrounding whitespace."""
        return self._WHITESPACE_PATTERN.sub(" ", value).strip()

