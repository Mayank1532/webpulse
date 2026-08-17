"""External API acquisition adapter."""

from __future__ import annotations

from mcp_liveops.acquisition.api_models import (
    ExternalApiResponse,
    ExternalApiStatus,
)
from mcp_liveops.acquisition.api_normalization import ExternalApiNormalizer
from mcp_liveops.acquisition.models import (
    AcquisitionResult,
    AcquisitionStatus,
)


class ExternalApiAcquirer:
    """Convert external API responses into acquisition results.

    This boundary deliberately contains no API credentials and performs
    no network requests. Concrete providers such as NewsAPI are connected
    later through a dedicated provider integration layer.
    """

    def __init__(
        self,
        normalizer: ExternalApiNormalizer | None = None,
    ) -> None:
        """Initialize the external API acquisition adapter."""
        self._normalizer = normalizer or ExternalApiNormalizer()

    def acquire(self, response: ExternalApiResponse) -> AcquisitionResult:
        """Normalize an external API response into acquisition evidence."""

        normalized = self._normalizer.normalize(response)

        if normalized is None:
            status = (
                AcquisitionStatus.EMPTY
                if response.status is ExternalApiStatus.EMPTY
                else AcquisitionStatus.FAILED
            )

            return AcquisitionResult(
                status=status,
                source_name=response.source_name or response.provider,
                source_uri=str(response.endpoint),
                message=(
                    "External API response contains no usable evidence."
                ),
            )

        return AcquisitionResult(
            status=AcquisitionStatus.SUCCESS,
            source_name=normalized.source_name,
            content=normalized.content,
            source_uri=str(normalized.endpoint),
            message="External API evidence acquired successfully.",
        )

