"""External API response normalization."""

from __future__ import annotations

import re

from mcp_liveops.acquisition.api_models import (
    ExternalApiResponse,
    ExternalApiStatus,
)


class ExternalApiNormalizer:
    """Normalize provider responses into stable text evidence."""

    _WHITESPACE_PATTERN = re.compile(r"\s+")

    def normalize(self, response: ExternalApiResponse) -> ExternalApiResponse | None:
        """Normalize an external API response.

        Returns None when the response contains no usable evidence.
        """

        if response.status is not ExternalApiStatus.SUCCESS:
            return None

        title = self._normalize_text(response.title)
        content = self._normalize_text(response.content)
        source_name = self._normalize_text(response.source_name)
        provider = self._normalize_text(response.provider)

        if not provider or not title or not content or not source_name:
            return None

        return response.model_copy(
            update={
                "provider": provider,
                "title": title,
                "content": content,
                "source_name": source_name,
                "message": "External API response normalized successfully.",
            }
        )

    def _normalize_text(self, value: str) -> str:
        """Normalize repeated and surrounding whitespace."""
        return self._WHITESPACE_PATTERN.sub(" ", value).strip()

