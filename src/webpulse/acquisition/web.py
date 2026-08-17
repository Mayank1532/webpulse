"""Provider-neutral web acquisition adapter."""

from __future__ import annotations

from webpulse.acquisition.document_models import WebDocument
from webpulse.acquisition.html_extractor import HTMLExtractor
from webpulse.acquisition.models import (
    AcquisitionResult,
    AcquisitionStatus,
)
from webpulse.acquisition.normalization import WebSourceNormalizer
from webpulse.acquisition.retrieval_models import WebRetrievalResult
from webpulse.acquisition.web_models import WebAcquisitionResult


class WebAcquirer:
    """Convert retrieved web resources into normalized acquisition results."""

    def __init__(
        self,
        normalizer: WebSourceNormalizer | None = None,
        extractor: HTMLExtractor | None = None,
    ) -> None:
        """Initialize the web acquisition adapter."""
        self._normalizer = normalizer or WebSourceNormalizer()
        self._extractor = extractor or HTMLExtractor()

    def acquire(self, result: WebAcquisitionResult) -> AcquisitionResult:
        """Normalize and convert a web provider result."""

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

    def acquire_retrieval(
        self,
        result: WebRetrievalResult,
    ) -> AcquisitionResult:
        """Convert a live retrieval result into an acquisition result."""

        if not result.succeeded:
            acquisition = AcquisitionResult(
                status=AcquisitionStatus.FAILED,
                source_name="unknown",
                source_uri=str(result.url) if result.url is not None else None,
                message=result.message,
            )

            return acquisition.model_copy(
                update={"retrieved_at": result.retrieved_at}
            )

        if result.url is None:
            acquisition = AcquisitionResult(
                status=AcquisitionStatus.FAILED,
                source_name="unknown",
                source_uri=None,
                message="Successful web retrieval did not contain a URL.",
            )

            return acquisition.model_copy(
                update={"retrieved_at": result.retrieved_at}
            )

        host = result.url.host or "unknown"

        document: WebDocument = self._extractor.extract(
            url=result.url,
            html=result.content,
            content_type=result.content_type,
        )

        if not document.usable:
            acquisition = AcquisitionResult(
                status=AcquisitionStatus.EMPTY,
                source_name=host,
                source_uri=str(result.url),
                message="Retrieved web page contains no usable text.",
            )

            return acquisition.model_copy(
                update={"retrieved_at": result.retrieved_at}
            )

        acquisition_result = WebAcquisitionResult(
            url=document.url,
            title=document.title or host,
            content=document.text,
            source_name=host,
        )

        acquisition = self.acquire(acquisition_result)

        return acquisition.model_copy(
            update={"retrieved_at": result.retrieved_at}
        )
