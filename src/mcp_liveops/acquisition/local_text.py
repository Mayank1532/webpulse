"""Local text-file evidence acquisition adapter."""

from __future__ import annotations

from pathlib import Path

from mcp_liveops.acquisition.interface import EvidenceAcquirer
from mcp_liveops.acquisition.models import (
    AcquisitionResult,
    AcquisitionStatus,
)


class LocalTextAcquirer(EvidenceAcquirer):
    """Acquire evidence from a local UTF-8 text file."""

    def acquire(self, source: str) -> AcquisitionResult:
        """Read a local text file deterministically."""

        path = Path(source)

        if not path.exists():
            return AcquisitionResult(
                status=AcquisitionStatus.FAILED,
                source_name=path.name or "unknown",
                message="Source file does not exist.",
            )

        if not path.is_file():
            return AcquisitionResult(
                status=AcquisitionStatus.FAILED,
                source_name=path.name or "unknown",
                message="Source path is not a file.",
            )

        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return AcquisitionResult(
                status=AcquisitionStatus.FAILED,
                source_name=path.name or "unknown",
                message="Source file is not valid UTF-8 text.",
            )
        except OSError as exc:
            return AcquisitionResult(
                status=AcquisitionStatus.FAILED,
                source_name=path.name or "unknown",
                message=f"Unable to read source file: {exc}",
            )

        normalized = content.strip()

        if not normalized:
            return AcquisitionResult(
                status=AcquisitionStatus.EMPTY,
                source_name=path.name or "unknown",
                source_uri=path.resolve().as_uri(),
                message="Source file contains no usable text.",
            )

        return AcquisitionResult(
            status=AcquisitionStatus.SUCCESS,
            source_name=path.name or "unknown",
            content=normalized,
            source_uri=path.resolve().as_uri(),
            message="Source text acquired successfully.",
        )

