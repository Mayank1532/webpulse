"""Controlled live HTTP web retrieval."""

from __future__ import annotations

from urllib.parse import urlparse

import httpx
from pydantic import HttpUrl, ValidationError

from webpulse.acquisition.retrieval_models import (
    RetrievalStatus,
    WebRetrievalResult,
)
from webpulse.config.settings import Settings


class WebRetriever:
    """Retrieve web resources through a controlled HTTP client."""

    def __init__(
        self,
        settings: Settings | None = None,
        client: httpx.Client | None = None,
    ) -> None:
        """Initialize the retriever with optional dependency injection."""
        self._settings = settings or Settings()
        self._client = client

    def retrieve(self, url: str) -> WebRetrievalResult:
        """Retrieve a web resource and return a structured result."""

        parsed = urlparse(url)

        if parsed.scheme not in {"http", "https"}:
            return self._invalid_url_result(
                url,
                "Only HTTP and HTTPS URLs are supported.",
            )

        if not parsed.netloc:
            return self._invalid_url_result(
                url,
                "URL must contain a valid host.",
            )

        try:
            validated_url = HttpUrl(url)
        except ValidationError:
            return self._invalid_url_result(
                url,
                "URL is not valid.",
            )

        try:
            if self._client is not None:
                response = self._client.get(
                    url,
                    follow_redirects=True,
                )
            else:
                with httpx.Client(
                    timeout=self._settings.web_timeout_seconds,
                    follow_redirects=True,
                    max_redirects=self._settings.web_max_redirects,
                ) as client:
                    response = client.get(url)

            content_length = response.headers.get("content-length")

            if content_length is not None:
                try:
                    declared_size = int(content_length)
                except ValueError:
                    declared_size = 0

                if declared_size > self._settings.web_max_response_bytes:
                    return self._failure(
                        validated_url,
                        "Response exceeds the configured size limit.",
                        status_code=response.status_code,
                        content_type=response.headers.get("content-type"),
                    )

            if response.status_code >= 400:
                return self._failure(
                    validated_url,
                    f"HTTP request failed with status {response.status_code}.",
                    status_code=response.status_code,
                    content_type=response.headers.get("content-type"),
                )

            content = response.content

            if len(content) > self._settings.web_max_response_bytes:
                return self._failure(
                    validated_url,
                    "Response exceeds the configured size limit.",
                    status_code=response.status_code,
                    content_type=response.headers.get("content-type"),
                )

            return WebRetrievalResult(
                status=RetrievalStatus.SUCCESS,
                url=validated_url,
                status_code=response.status_code,
                content_type=response.headers.get("content-type"),
                content=response.text,
                message="Web resource retrieved successfully.",
            )

        except httpx.TimeoutException:
            return self._failure(
                validated_url,
                "Web request timed out.",
            )

        except httpx.RequestError as exc:
            return self._failure(
                validated_url,
                f"Web request failed: {exc.__class__.__name__}.",
            )

    def _invalid_url_result(
        self,
        url: str,
        message: str,
    ) -> WebRetrievalResult:
        """Create a structured result for an invalid URL."""

        return WebRetrievalResult(
            status=RetrievalStatus.FAILED,
            url=None,
            message=f"{message} Received URL: {url}",
        )

    def _failure(
        self,
        url: HttpUrl,
        message: str,
        *,
        status_code: int | None = None,
        content_type: str | None = None,
    ) -> WebRetrievalResult:
        """Create a failed retrieval result."""

        return WebRetrievalResult(
            status=RetrievalStatus.FAILED,
            url=url,
            status_code=status_code,
            content_type=content_type,
            message=message,
        )