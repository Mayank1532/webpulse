import pytest
from pydantic import ValidationError

from mcp_liveops.acquisition import (
    AcquisitionStatus,
    WebAcquirer,
    WebAcquisitionResult,
    WebSourceNormalizer,
)


def make_result(
    *,
    title: str = "Example Source",
    content: str = "Example evidence content.",
    source_name: str = "Example",
) -> WebAcquisitionResult:
    return WebAcquisitionResult(
        url="https://example.com/evidence",
        title=title,
        content=content,
        source_name=source_name,
    )


def test_web_source_normalizer_normalizes_whitespace() -> None:
    result = make_result(
        title="  Example   Source  ",
        content=" Evidence   with\nmultiple\tspaces. ",
        source_name="  Example   Site ",
    )

    normalized = WebSourceNormalizer().normalize(result)

    assert normalized is not None
    assert normalized.title == "Example Source"
    assert normalized.content == "Evidence with multiple spaces."
    assert normalized.source_name == "Example Site"
    assert str(normalized.url) == "https://example.com/evidence"


def test_web_source_normalizer_returns_none_for_empty_content() -> None:
    result = make_result(content="   ")

    normalized = WebSourceNormalizer().normalize(result)

    assert normalized is None


def test_web_source_normalizer_returns_none_for_empty_title() -> None:
    result = make_result(title="   ")

    normalized = WebSourceNormalizer().normalize(result)

    assert normalized is None


def test_web_source_normalizer_returns_none_for_empty_source_name() -> None:
    result = make_result(source_name="   ")

    normalized = WebSourceNormalizer().normalize(result)

    assert normalized is None


def test_web_acquirer_returns_success_for_valid_result() -> None:
    result = make_result()

    acquisition = WebAcquirer().acquire(result)

    assert acquisition.status is AcquisitionStatus.SUCCESS
    assert acquisition.succeeded is True
    assert acquisition.source_name == "Example"
    assert acquisition.content == "Example evidence content."
    assert acquisition.source_uri == "https://example.com/evidence"
    assert acquisition.message == "Web evidence normalized successfully."


def test_web_acquirer_returns_empty_for_unusable_result() -> None:
    result = make_result(content="")

    acquisition = WebAcquirer().acquire(result)

    assert acquisition.status is AcquisitionStatus.EMPTY
    assert acquisition.succeeded is False
    assert acquisition.message == "Web result contains no usable evidence."


def test_web_result_rejects_invalid_url() -> None:
    with pytest.raises(ValidationError):
        WebAcquisitionResult(
            url="not-a-url",
            title="Example",
            content="Content",
            source_name="Example",
        )


def test_web_result_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError):
        WebAcquisitionResult(
            url="https://example.com",
            title="Example",
            content="Content",
            source_name="Example",
            unexpected="value",
        )


def test_web_result_is_immutable() -> None:
    result = make_result()

    with pytest.raises(ValidationError):
        result.title = "Changed"


def test_web_normalization_is_deterministic() -> None:
    result = make_result(
        title=" Example   Source ",
        content=" Some   content ",
        source_name=" Example ",
    )

    normalizer = WebSourceNormalizer()

    first = normalizer.normalize(result)
    second = normalizer.normalize(result)

    assert first == second


def test_web_acquirer_uses_injected_normalizer() -> None:
    class FixedNormalizer(WebSourceNormalizer):
        def normalize(self, result: WebAcquisitionResult):
            return super().normalize(
                result.model_copy(
                    update={
                        "title": "Injected Title",
                    }
                )
            )

    result = make_result()

    acquisition = WebAcquirer(
        normalizer=FixedNormalizer()
    ).acquire(result)

    assert acquisition.status is AcquisitionStatus.SUCCESS
    assert acquisition.source_name == "Example"
    assert acquisition.content == "Example evidence content."

