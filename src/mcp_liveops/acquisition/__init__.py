"""Evidence acquisition package."""

from mcp_liveops.acquisition.api_models import (
    ExternalApiResponse,
    ExternalApiStatus,
)
from mcp_liveops.acquisition.api_normalization import ExternalApiNormalizer
from mcp_liveops.acquisition.external_api import ExternalApiAcquirer
from mcp_liveops.acquisition.interface import EvidenceAcquirer
from mcp_liveops.acquisition.local_text import LocalTextAcquirer
from mcp_liveops.acquisition.models import (
    AcquisitionResult,
    AcquisitionStatus,
)
from mcp_liveops.acquisition.normalization import WebSourceNormalizer
from mcp_liveops.acquisition.web import WebAcquirer
from mcp_liveops.acquisition.web_models import (
    WebAcquisitionResult,
    WebSource,
)

__all__ = [
    "AcquisitionResult",
    "AcquisitionStatus",
    "EvidenceAcquirer",
    "ExternalApiAcquirer",
    "ExternalApiNormalizer",
    "ExternalApiResponse",
    "ExternalApiStatus",
    "LocalTextAcquirer",
    "WebAcquirer",
    "WebAcquisitionResult",
    "WebSource",
    "WebSourceNormalizer",
]

