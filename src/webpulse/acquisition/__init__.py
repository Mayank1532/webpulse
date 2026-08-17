"""Web acquisition package."""

from webpulse.acquisition.document_models import WebDocument
from webpulse.acquisition.html_extractor import HTMLExtractor
from webpulse.acquisition.interface import EvidenceAcquirer
from webpulse.acquisition.models import (
    AcquisitionResult,
    AcquisitionStatus,
)
from webpulse.acquisition.normalization import WebSourceNormalizer
from webpulse.acquisition.retrieval_models import (
    RetrievalStatus,
    WebRetrievalResult,
)
from webpulse.acquisition.retriever import WebRetriever
from webpulse.acquisition.web import WebAcquirer
from webpulse.acquisition.web_models import (
    WebAcquisitionResult,
    WebSource,
)

__all__ = [
    "AcquisitionResult",
    "AcquisitionStatus",
    "EvidenceAcquirer",
    "HTMLExtractor",
    "RetrievalStatus",
    "WebAcquirer",
    "WebAcquisitionResult",
    "WebDocument",
    "WebRetrievalResult",
    "WebRetriever",
    "WebSource",
    "WebSourceNormalizer",
]
