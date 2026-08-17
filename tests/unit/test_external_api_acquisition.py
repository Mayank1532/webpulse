import pytest
from pydantic import ValidationError

from mcp_liveops.acquisition import (
    AcquisitionStatus,
    ExternalApiAcquirer,
    ExternalApiNormalizer,
    ExternalApiResponse,
    ExternalApiStatus,
)


def make_response(
    *,
    provider: str = "NewsAPI",
    title: str = "Example Article",
    content: str = "Example article content.",
    source_name: str = "Example News",
    status: ExternalApiStatus = ExternalApiStatus.SUCCESS,
) -> ExternalApiResponse:
    return ExternalApiResponse(
        provider=provider,
        endpoint="https://example.com/v1/articles",
        title=title,
        content=content,
        source_name=source_name,
        status=status,
        message="Provider response received.",
    )


def test_external_api_normalizer_normalizes_text() -> None:
    response = make_response(
        title="  Example   Article ",
        content=" Article   content\nwith\tspaces. ",
        source_name="  Example   News ",
        provider="  NewsAPI ",
    )

    normalized = ExternalApiNormalizer().normalize(response)

    assert normalized is not None
    assert normalized.provider == "NewsAPI"
    assert normalized.title == "Example Article"
    assert normalized.content == "Article content with spaces."
    assert normalized.source_name == "Example News"


def test_external_api_normalizer_returns_none_for_empty_content() -> None:
    response = make_response(content="   ")

    normalized = ExternalApiNormalizer().normalize(response)

    assert normalized is None


def test_external_api_normalizer_returns_none_for_empty_title() -> None:
    response = make_response(title="   ")

    normalized = ExternalApiNormalizer().normalize(response)

    assert normalized is None


def test_external_api_normalizer_returns_none_for_empty_source() -> None:
    response = make_response(source_name="   ")

    normalized = ExternalApiNormalizer().normalize(response)

    assert normalized is None


def test_external_api_normalizer_rejects_failed_response() -> None:
    response = make_response(
        status=ExternalApiStatus.FAILED,
        content="Error payload",
    )

    normalized = ExternalApiNormalizer().normalize(response)

    assert normalized is None


def test_external_api_normalizer_rejects_empty_response() -> None:
    response = make_response(
        status=ExternalApiStatus.EMPTY,
        content="",
    )

    normalized = ExternalApiNormalizer().normalize(response)

    assert normalized is None


def test_external_api_acquirer_returns_success() -> None:
    response = make_response()

    result = ExternalApiAcquirer().acquire(response)

    assert result.status is AcquisitionStatus.SUCCESS
    assert result.succeeded is True
    assert result.source_name == "Example News"
    assert result.content == "Example article content."
    assert result.source_uri == "https://example.com/v1/articles"
    assert result.message == "External API evidence acquired successfully."


def test_external_api_acquirer_returns_empty_for_empty_response() -> None:
    response = make_response(
        status=ExternalApiStatus.EMPTY,
        content="",
    )

    result = ExternalApiAcquirer().acquire(response)

    assert result.status is AcquisitionStatus.EMPTY
    assert result.succeeded is False
    assert result.message == "External API response contains no usable evidence."


def test_external_api_acquirer_returns_failed_for_failed_response() -> None:
    response = make_response(
        status=ExternalApiStatus.FAILED,
        content="",
    )

    result = ExternalApiAcquirer().acquire(response)

    assert result.status is AcquisitionStatus.FAILED
    assert result.succeeded is False
    assert result.message == "External API response contains no usable evidence."


def test_external_api_response_rejects_invalid_endpoint() -> None:
    with pytest.raises(ValidationError):
        ExternalApiResponse(
            provider="NewsAPI",
            endpoint="not-a-url",
            title="Example",
            content="Content",
            source_name="Example News",
            status=ExternalApiStatus.SUCCESS,
            message="Received.",
        )


def test_external_api_response_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError):
        ExternalApiResponse(
            provider="NewsAPI",
            endpoint="https://example.com",
            title="Example",
            content="Content",
            source_name="Example News",
            status=ExternalApiStatus.SUCCESS,
            message="Received.",
            unexpected="value",
        )


def test_external_api_response_is_immutable() -> None:
    response = make_response()

    with pytest.raises(ValidationError):
        response.title = "Changed"


def test_external_api_normalization_is_deterministic() -> None:
    response = make_response(
        title=" Example ",
        content=" Content ",
        source_name=" Example News ",
        provider=" NewsAPI ",
    )

    normalizer = ExternalApiNormalizer()

    first = normalizer.normalize(response)
    second = normalizer.normalize(response)

    assert first == second

