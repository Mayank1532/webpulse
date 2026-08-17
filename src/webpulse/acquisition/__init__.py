"""Web acquisition package."""

from webpulse.acquisition.interface import EvidenceAcquirer
from webpulse.acquisition.models import (
    AcquisitionResult,
    AcquisitionStatus,
)
from webpulse.acquisition.normalization import WebSourceNormalizer
from webpulse.acquisition.web import WebAcquirer
from webpulse.acquisition.web_models import (
    WebAcquisitionResult,
    WebSource,
)

__all__ = [
    "AcquisitionResult",
    "AcquisitionStatus",
    "EvidenceAcquirer",
    "WebAcquirer",
    "WebAcquisitionResult",
    "WebSource",
    "WebSourceNormalizer",
]
