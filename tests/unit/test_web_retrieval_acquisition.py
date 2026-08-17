"""Tests for retrieval-to-extraction acquisition integration."""

from datetime import datetime, timezone
from unittest.mock import Mock

from webpulse.acquisition import (
    AcquisitionStatus,
    HTMLExtractor,
    RetrievalStatus,
    WebAcquirer,
    WebRetrievalResult,
)

FIXED_RETRIEVED_AT = datetime(
    2026,
    8,
    17,
    12,
    0,
    0,
    tzinfo=timezone.utc,
)


def make_successful_retrieval(
    *,
    content: str = """
        <html>
            <head>
                <title>WEBPULSE Article</title>
            </head>
            <body>
                <nav>Navigation</nav>
                <main>
                    <h1>Live Web Intelligence</h1>
                    <p>Important retrieved content.</p>
                </main>
                <footer>Footer</footer>
            </body>
        </html>
    """,
) -> WebRetrievalResult:
    """Create a deterministic successful retrieval result."""
    return WebRetrievalResult(
        status=RetrievalStatus.SUCCESS,
        url="https://example.com/article",
        status_code=200,
        content_type="text/html",
        content=content,
        retrieved_at=FIXED_RETRIEVED_AT,
        message="Web resource retrieved successfully.",
    )


def test_acquire_retrieval_extracts_html_into_acquisition_result() -> None:
    result = make_successful_retrieval()

    acquisition = WebAcquirer().acquire_retrieval(result)

    assert acquisition.status is AcquisitionStatus.SUCCESS
    assert acquisition.succeeded is True
    assert acquisition.source_name == "example.com"
    assert acquisition.source_uri == "https://example.com/article"
    assert acquisition.content == (
        "WEBPULSE Article Live Web Intelligence Important retrieved content."
    )
    assert acquisition.message == "Web evidence normalized successfully."


def test_acquire_retrieval_removes_html_noise() -> None:
    result = make_successful_retrieval(
        content="""
            <html>
                <head>
                    <title>Clean Article</title>
                    <script>
                        const secret = "must not appear";
                    </script>
                </head>
                <body>
                    <nav>Navigation Noise</nav>
                    <main>
                        <p>Useful article text.</p>
                    </main>
                    <footer>Footer Noise</footer>
                </body>
            </html>
        """
    )

    acquisition = WebAcquirer().acquire_retrieval(result)

    assert acquisition.status is AcquisitionStatus.SUCCESS
    assert acquisition.content == "Clean Article Useful article text."
    assert "Navigation Noise" not in acquisition.content
    assert "Footer Noise" not in acquisition.content
    assert "must not appear" not in acquisition.content


def test_failed_retrieval_does_not_call_extractor() -> None:
    extractor = Mock(spec=HTMLExtractor)

    result = WebRetrievalResult(
        status=RetrievalStatus.FAILED,
        url="https://example.com/article",
        status_code=503,
        content_type="text/html",
        message="HTTP request failed with status 503.",
        retrieved_at=FIXED_RETRIEVED_AT,
    )

    acquisition = WebAcquirer(extractor=extractor).acquire_retrieval(result)

    assert acquisition.status is AcquisitionStatus.FAILED
    assert acquisition.succeeded is False
    assert acquisition.source_name == "unknown"
    assert acquisition.source_uri == "https://example.com/article"
    assert acquisition.message == "HTTP request failed with status 503."
    extractor.extract.assert_not_called()


def test_failed_retrieval_without_url_is_handled() -> None:
    result = WebRetrievalResult(
        status=RetrievalStatus.FAILED,
        url=None,
        message="URL is not valid.",
        retrieved_at=FIXED_RETRIEVED_AT,
    )

    acquisition = WebAcquirer().acquire_retrieval(result)

    assert acquisition.status is AcquisitionStatus.FAILED
    assert acquisition.succeeded is False
    assert acquisition.source_uri is None
    assert acquisition.message == "URL is not valid."


def test_successful_retrieval_without_url_is_rejected() -> None:
    result = WebRetrievalResult(
        status=RetrievalStatus.SUCCESS,
        url=None,
        status_code=200,
        content_type="text/html",
        content="<html><body>Content</body></html>",
        message="Web resource retrieved successfully.",
        retrieved_at=FIXED_RETRIEVED_AT,
    )

    acquisition = WebAcquirer().acquire_retrieval(result)

    assert acquisition.status is AcquisitionStatus.FAILED
    assert acquisition.succeeded is False
    assert acquisition.source_uri is None
    assert (
        acquisition.message
        == "Successful web retrieval did not contain a URL."
    )


def test_empty_retrieved_html_returns_empty_result() -> None:
    result = make_successful_retrieval(content="")

    acquisition = WebAcquirer().acquire_retrieval(result)

    assert acquisition.status is AcquisitionStatus.EMPTY
    assert acquisition.succeeded is False
    assert acquisition.source_name == "example.com"
    assert acquisition.source_uri == "https://example.com/article"
    assert acquisition.message == "Retrieved web page contains no usable text."


def test_acquire_retrieval_supports_injected_extractor() -> None:
    extractor = Mock(spec=HTMLExtractor)
    extractor.extract.return_value = HTMLExtractor().extract(
        url="https://example.com/article",
        html="""
            <html>
                <head>
                    <title>Injected</title>
                </head>
                <body>
                    <p>Injected extractor content.</p>
                </body>
            </html>
        """,
        content_type="text/html",
    )

    result = make_successful_retrieval()

    acquisition = WebAcquirer(
        extractor=extractor,
    ).acquire_retrieval(result)

    assert acquisition.status is AcquisitionStatus.SUCCESS
    assert acquisition.content == "Injected Injected extractor content."
    extractor.extract.assert_called_once()


def test_acquire_retrieval_is_deterministic() -> None:
    result = make_successful_retrieval()

    acquirer = WebAcquirer()

    first = acquirer.acquire_retrieval(result)
    second = acquirer.acquire_retrieval(result)

    assert first == second
    assert first.retrieved_at == second.retrieved_at
    assert first.retrieved_at == FIXED_RETRIEVED_AT
