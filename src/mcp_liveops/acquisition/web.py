"""Provider-neutral web acquisition adapter."""

from __future__ import annotations

from mcp_liveops.acquisition.models import (
    AcquisitionResult,
    AcquisitionStatus,
)
from mcp_liveops.acquisition.normalization import WebSourceNormalizer
from mcp_liveops.acquisition.web_models import WebAcquisitionResult


class WebAcquirer:
    """Convert normalized web results into acquisition results.

    External providers such as Tavily will be connected outside this
    boundary. This class deliberately contains no API credentials.
    """

    def __init__(self, normalizer: WebSourceNormalizer | None = None) -> None:
        """Initialize the web acquisition adapter."""
        self._normalizer = normalizer or WebSourceNormalizer()

    def acquire(self, result: WebAcquisitionResult) -> AcquisitionResult:
        """Normalize and convert a provider result."""

        source = self._normalizer.normalize(result)

        if source is None:
            return AcquisitionResult(
                status=AcquisitionStatus.EMPTY,
                source_name=result.source_name or "unknown",
                source_uri=str(result.url),
                message="Web result contains no usable evidence.",
            )

        return AcquisitionResult(
            status=AcquisitionStatus.SUCCESS,
            source_name=source.source_name,
            content=source.content,
            source_uri=str(source.url),
            message="Web evidence normalized successfully.",
        )

