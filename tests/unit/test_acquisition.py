from pathlib import Path

from mcp_liveops.acquisition import (
    AcquisitionStatus,
    EvidenceAcquirer,
    LocalTextAcquirer,
)


def test_local_text_acquisition_succeeds(tmp_path: Path) -> None:
    source = tmp_path / "evidence.txt"
    source.write_text(
        "Important evidence content.",
        encoding="utf-8",
    )

    result = LocalTextAcquirer().acquire(str(source))

    assert result.status is AcquisitionStatus.SUCCESS
    assert result.succeeded is True
    assert result.content == "Important evidence content."
    assert result.source_name == "evidence.txt"
    assert result.source_uri is not None


def test_local_text_acquisition_trims_content(tmp_path: Path) -> None:
    source = tmp_path / "evidence.txt"
    source.write_text(
        "  evidence with surrounding whitespace  ",
        encoding="utf-8",
    )

    result = LocalTextAcquirer().acquire(str(source))

    assert result.content == "evidence with surrounding whitespace"


def test_missing_file_returns_failed_result(tmp_path: Path) -> None:
    source = tmp_path / "missing.txt"

    result = LocalTextAcquirer().acquire(str(source))

    assert result.status is AcquisitionStatus.FAILED
    assert result.succeeded is False
    assert result.message == "Source file does not exist."


def test_directory_returns_failed_result(tmp_path: Path) -> None:
    result = LocalTextAcquirer().acquire(str(tmp_path))

    assert result.status is AcquisitionStatus.FAILED
    assert result.succeeded is False
    assert result.message == "Source path is not a file."


def test_empty_file_returns_empty_result(tmp_path: Path) -> None:
    source = tmp_path / "empty.txt"
    source.write_text("", encoding="utf-8")

    result = LocalTextAcquirer().acquire(str(source))

    assert result.status is AcquisitionStatus.EMPTY
    assert result.succeeded is False
    assert result.message == "Source file contains no usable text."


def test_invalid_utf8_returns_failed_result(tmp_path: Path) -> None:
    source = tmp_path / "invalid.txt"
    source.write_bytes(b"valid text\xff\xfe")

    result = LocalTextAcquirer().acquire(str(source))

    assert result.status is AcquisitionStatus.FAILED
    assert result.succeeded is False
    assert result.message == "Source file is not valid UTF-8 text."


def test_acquisition_interface_is_implemented() -> None:
    acquirer = LocalTextAcquirer()

    assert isinstance(acquirer, EvidenceAcquirer)

