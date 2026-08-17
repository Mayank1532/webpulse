"""Tests for controlled live web retrieval."""

from unittest.mock import Mock

import httpx

from webpulse.acquisition.retrieval_models import RetrievalStatus
from webpulse.acquisition.retriever import WebRetriever
from webpulse.config.settings import Settings


def make_response(
    *,
    status_code: int = 200,
    content: bytes = b"<html><body>Hello WEBPULSE</body></html>",
    content_type: str = "text/html",
    headers: dict[str, str] | None = None,
) -> httpx.Response:
    """Create a deterministic HTTP response."""
    response_headers = {
        "content-type": content_type,
        **(headers or {}),
    }

    return httpx.Response(
        status_code=status_code,
        headers=response_headers,
        content=content,
        request=httpx.Request("GET", "https://example.com"),
    )


def test_successful_retrieval() -> None:
    client = Mock()
    client.get.return_value = make_response()

    retriever = WebRetriever(client=client)

    result = retriever.retrieve("https://example.com")

    assert result.status is RetrievalStatus.SUCCESS
    assert result.succeeded is True
    assert result.status_code == 200
    assert result.content_type == "text/html"
    assert result.content == "<html><body>Hello WEBPULSE</body></html>"
    assert str(result.url) == "https://example.com/"

    client.get.assert_called_once_with(
        "https://example.com",
        follow_redirects=True,
    )


def test_http_error_returns_failed_result() -> None:
    client = Mock()
    client.get.return_value = make_response(
        status_code=404,
        content=b"Not found",
    )

    retriever = WebRetriever(client=client)

    result = retriever.retrieve("https://example.com/missing")

    assert result.status is RetrievalStatus.FAILED
    assert result.succeeded is False
    assert result.status_code == 404
    assert result.message == "HTTP request failed with status 404."


def test_server_error_returns_failed_result() -> None:
    client = Mock()
    client.get.return_value = make_response(
        status_code=503,
        content=b"Unavailable",
    )

    retriever = WebRetriever(client=client)

    result = retriever.retrieve("https://example.com")

    assert result.status is RetrievalStatus.FAILED
    assert result.status_code == 503
    assert result.message == "HTTP request failed with status 503."


def test_timeout_returns_failed_result() -> None:
    client = Mock()
    client.get.side_effect = httpx.ReadTimeout(
        "request timed out",
        request=httpx.Request("GET", "https://example.com"),
    )

    retriever = WebRetriever(client=client)

    result = retriever.retrieve("https://example.com")

    assert result.status is RetrievalStatus.FAILED
    assert result.succeeded is False
    assert result.message == "Web request timed out."
    assert str(result.url) == "https://example.com/"


def test_request_error_returns_failed_result() -> None:
    client = Mock()
    client.get.side_effect = httpx.ConnectError(
        "connection failed",
        request=httpx.Request("GET", "https://example.com"),
    )

    retriever = WebRetriever(client=client)

    result = retriever.retrieve("https://example.com")

    assert result.status is RetrievalStatus.FAILED
    assert result.message == "Web request failed: ConnectError."
    assert str(result.url) == "https://example.com/"


def test_non_http_scheme_is_rejected_without_network_call() -> None:
    client = Mock()

    retriever = WebRetriever(client=client)

    result = retriever.retrieve("ftp://example.com/file.txt")

    assert result.status is RetrievalStatus.FAILED
    assert result.url is None
    assert result.message.startswith(
        "Only HTTP and HTTPS URLs are supported."
    )
    client.get.assert_not_called()


def test_missing_host_is_rejected_without_network_call() -> None:
    client = Mock()

    retriever = WebRetriever(client=client)

    result = retriever.retrieve("https:///missing-host")

    assert result.status is RetrievalStatus.FAILED
    assert result.url is None
    assert result.message.startswith(
        "URL must contain a valid host."
    )
    client.get.assert_not_called()


def test_invalid_url_is_rejected_without_network_call() -> None:
    client = Mock()

    retriever = WebRetriever(client=client)

    result = retriever.retrieve("https://")

    assert result.status is RetrievalStatus.FAILED
    assert result.url is None
    assert result.message.startswith("URL must contain a valid host.")
    client.get.assert_not_called()


def test_declared_response_size_limit_is_enforced() -> None:
    client = Mock()
    client.get.return_value = make_response(
        headers={"content-length": "1000"},
    )

    settings = Settings(web_max_response_bytes=500)

    retriever = WebRetriever(
        settings=settings,
        client=client,
    )

    result = retriever.retrieve("https://example.com")

    assert result.status is RetrievalStatus.FAILED
    assert result.message == "Response exceeds the configured size limit."
    assert result.status_code == 200


def test_actual_response_size_limit_is_enforced() -> None:
    client = Mock()
    client.get.return_value = make_response(
        content=b"x" * 1001,
    )

    settings = Settings(web_max_response_bytes=1000)

    retriever = WebRetriever(
        settings=settings,
        client=client,
    )

    result = retriever.retrieve("https://example.com")

    assert result.status is RetrievalStatus.FAILED
    assert result.message == "Response exceeds the configured size limit."
    assert result.status_code == 200


def test_invalid_content_length_does_not_break_retrieval() -> None:
    client = Mock()
    client.get.return_value = make_response(
        headers={"content-length": "not-a-number"},
    )

    retriever = WebRetriever(client=client)

    result = retriever.retrieve("https://example.com")

    assert result.status is RetrievalStatus.SUCCESS
    assert result.content == "<html><body>Hello WEBPULSE</body></html>"
