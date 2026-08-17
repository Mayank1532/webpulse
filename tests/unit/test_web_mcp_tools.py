"""Tests for the MCP web retrieval tool."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from webpulse.acquisition import (
    RetrievalStatus,
    WebRetrievalResult,
)
from webpulse.mcp.web_tools import (
    WEB_RETRIEVE_DESCRIPTION,
    WEB_RETRIEVE_TOOL_NAME,
    WebMcpTools,
)

FIXED_RETRIEVED_AT = datetime(
    2026,
    8,
    17,
    12,
    0,
    tzinfo=timezone.utc,
)


class FakeWebRetriever:
    """Deterministic web retriever test double."""

    def __init__(
        self,
        result: WebRetrievalResult,
    ) -> None:
        self.result = result
        self.urls: list[str] = []

    def retrieve(self, url: str) -> WebRetrievalResult:
        """Return the configured result without network access."""
        self.urls.append(url)
        return self.result


def make_success_result() -> WebRetrievalResult:
    """Create a deterministic successful retrieval result."""
    return WebRetrievalResult(
        status=RetrievalStatus.SUCCESS,
        url="https://example.com/article",
        status_code=200,
        content_type="text/html",
        content="<html><body>Example article content.</body></html>",
        retrieved_at=FIXED_RETRIEVED_AT,
        message="Web retrieval succeeded.",
    )


def make_failure_result() -> WebRetrievalResult:
    """Create a deterministic failed retrieval result."""
    return WebRetrievalResult(
        status=RetrievalStatus.FAILED,
        url="https://example.com/article",
        status_code=500,
        content_type="text/html",
        content="",
        retrieved_at=FIXED_RETRIEVED_AT,
        message="Web retrieval failed.",
    )


def test_metadata_has_expected_tool_name() -> None:
    """The MCP tool metadata should expose the locked tool name."""
    tools = WebMcpTools(
        retriever=FakeWebRetriever(make_success_result())
    )

    metadata = tools.metadata()

    assert metadata.name == WEB_RETRIEVE_TOOL_NAME
    assert metadata.name == "web_retrieve"


def test_metadata_has_expected_description() -> None:
    """The MCP tool metadata should expose the controlled web description."""
    tools = WebMcpTools(
        retriever=FakeWebRetriever(make_success_result())
    )

    metadata = tools.metadata()

    assert metadata.description == WEB_RETRIEVE_DESCRIPTION
    assert "live web" in metadata.description


def test_metadata_has_web_category() -> None:
    """The tool should be classified as a web tool."""
    tools = WebMcpTools(
        retriever=FakeWebRetriever(make_success_result())
    )

    assert tools.metadata().category == "web"


def test_retrieve_returns_json_string() -> None:
    """The MCP boundary should return a JSON string."""
    expected = make_success_result()
    retriever = FakeWebRetriever(expected)
    tools = WebMcpTools(retriever=retriever)

    result = tools.retrieve(
        "https://example.com/article"
    )

    assert isinstance(result, str)

    payload = json.loads(result)

    assert payload["status"] == "success"
    assert payload["status_code"] == 200
    assert payload["url"] == "https://example.com/article"


def test_retrieve_passes_exact_url_to_retriever() -> None:
    """The MCP boundary should pass the URL unchanged."""
    retriever = FakeWebRetriever(make_success_result())
    tools = WebMcpTools(retriever=retriever)

    tools.retrieve(
        "https://example.com/article?topic=python"
    )

    assert retriever.urls == [
        "https://example.com/article?topic=python"
    ]


def test_retrieve_propagates_failure_as_json() -> None:
    """Retriever failures should remain visible through the MCP boundary."""
    expected = make_failure_result()
    retriever = FakeWebRetriever(expected)
    tools = WebMcpTools(retriever=retriever)

    result = tools.retrieve(
        "https://example.com/article"
    )

    payload = json.loads(result)

    assert payload["status"] == "failed"
    assert payload["status_code"] == 500
    assert payload["message"] == "Web retrieval failed."


def test_retrieve_serialization_is_deterministic() -> None:
    """The same deterministic retrieval should produce identical JSON."""
    expected = make_success_result()
    retriever = FakeWebRetriever(expected)
    tools = WebMcpTools(retriever=retriever)

    first = tools.retrieve(
        "https://example.com/article"
    )
    second = tools.retrieve(
        "https://example.com/article"
    )

    assert first == second


def test_retrieve_json_keys_are_sorted() -> None:
    """The MCP JSON serialization should remain deterministically ordered."""
    retriever = FakeWebRetriever(make_success_result())
    tools = WebMcpTools(retriever=retriever)

    result = tools.retrieve(
        "https://example.com/article"
    )

    keys = list(json.loads(result).keys())

    assert keys == sorted(keys)


def test_retrieve_dependency_injection() -> None:
    """The retriever dependency should be injectable."""
    expected = make_success_result()
    fake = FakeWebRetriever(expected)

    tools = WebMcpTools(retriever=fake)

    result = tools.retrieve(
        "https://example.com/article"
    )

    assert json.loads(result)["status"] == "success"
    assert fake.urls == ["https://example.com/article"]


def test_retrieve_does_not_make_network_requests() -> None:
    """The test double proves the MCP boundary needs no live network."""
    expected = make_success_result()
    fake = FakeWebRetriever(expected)

    tools = WebMcpTools(retriever=fake)

    tools.retrieve(
        "https://example.com/article"
    )

    assert len(fake.urls) == 1


def test_retrieve_preserves_retrieval_timestamp() -> None:
    """Structured JSON should preserve the deterministic retrieval timestamp."""
    retriever = FakeWebRetriever(make_success_result())
    tools = WebMcpTools(retriever=retriever)

    result = tools.retrieve(
        "https://example.com/article"
    )

    payload = json.loads(result)

    assert payload["retrieved_at"] == "2026-08-17T12:00:00Z"
