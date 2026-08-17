"""Deterministic HTML content extraction."""

from __future__ import annotations

import re

from bs4 import BeautifulSoup
from pydantic import HttpUrl

from webpulse.acquisition.document_models import WebDocument


class HTMLExtractor:
    """Extract useful textual content from HTML documents."""

    _WHITESPACE_PATTERN = re.compile(r"\s+")

    _REMOVE_TAGS = (
        "script",
        "style",
        "noscript",
        "template",
        "svg",
    )

    _NOISE_TAGS = (
        "nav",
        "footer",
        "header",
        "aside",
        "form",
    )

    def extract(
        self,
        *,
        url: HttpUrl,
        html: str,
        content_type: str | None = None,
    ) -> WebDocument:
        """Extract title and readable text from HTML."""

        soup = BeautifulSoup(html, "html.parser")

        for tag_name in self._REMOVE_TAGS:
            for tag in soup.find_all(tag_name):
                tag.decompose()

        for tag_name in self._NOISE_TAGS:
            for tag in soup.find_all(tag_name):
                tag.decompose()

        title = self._normalize_text(
            soup.title.get_text(" ", strip=True)
            if soup.title is not None
            else ""
        )

        text = self._normalize_text(
            soup.get_text(" ", strip=True)
        )

        return WebDocument(
            url=url,
            title=title,
            text=text,
            content_type=content_type,
        )

    def _normalize_text(self, value: str) -> str:
        """Normalize repeated whitespace."""
        return self._WHITESPACE_PATTERN.sub(" ", value).strip()
