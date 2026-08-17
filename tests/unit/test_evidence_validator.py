from datetime import datetime, timedelta, timezone

import pytest

from mcp_liveops.evidence import (
    EvidenceRecord,
    EvidenceValidator,
    RetrievalMethod,
    SourceType,
    ValidationReason,
    ValidationStatus,
)


def make_evidence(
    *,
    retrieved_at: datetime,
    published_at: datetime | None = None,
) -> EvidenceRecord:
    return EvidenceRecord(
        claim="A deterministic evidence claim.",
        content="Supporting evidence content.",
        source_name="Example Source",
        source_type=SourceType.WEB,
        retrieval_method=RetrievalMethod.WEB_REQUEST,
        retrieved_at=retrieved_at,
        published_at=published_at,
        source_reliability=0.9,
        confidence=0.9,
        validation_status=ValidationStatus.UNVERIFIED,
    )


def test_valid_evidence_passes() -> None:
    now = datetime.now(timezone.utc)
    evidence = make_evidence(retrieved_at=now - timedelta(hours=1))

    result = EvidenceValidator().validate(evidence, now=now)

    assert result.valid is True
    assert result.reason is ValidationReason.VALID
    assert result.stale is False


def test_future_retrieval_time_is_rejected() -> None:
    now = datetime.now(timezone.utc)
    evidence = make_evidence(retrieved_at=now + timedelta(minutes=1))

    result = EvidenceValidator().validate(evidence, now=now)

    assert result.valid is False
    assert result.reason is ValidationReason.FUTURE_RETRIEVAL_TIME


def test_future_publication_time_is_rejected() -> None:
    now = datetime.now(timezone.utc)
    evidence = make_evidence(
        retrieved_at=now - timedelta(hours=1),
        published_at=now + timedelta(minutes=1),
    )

    result = EvidenceValidator().validate(evidence, now=now)

    assert result.valid is False
    assert result.reason is ValidationReason.FUTURE_PUBLICATION_TIME


def test_publication_after_retrieval_is_rejected() -> None:
    now = datetime.now(timezone.utc)
    evidence = make_evidence(
        retrieved_at=now - timedelta(hours=1),
        published_at=now - timedelta(minutes=30),
    )

    result = EvidenceValidator().validate(evidence, now=now)

    assert result.valid is False
    assert result.reason is ValidationReason.PUBLICATION_AFTER_RETRIEVAL


def test_old_evidence_is_marked_stale() -> None:
    now = datetime.now(timezone.utc)
    evidence = make_evidence(retrieved_at=now - timedelta(days=31))

    validator = EvidenceValidator(stale_after=timedelta(days=30))
    result = validator.validate(evidence, now=now)

    assert result.valid is True
    assert result.stale is True
    assert result.reason is ValidationReason.STALE


def test_custom_stale_threshold_is_supported() -> None:
    now = datetime.now(timezone.utc)
    evidence = make_evidence(retrieved_at=now - timedelta(hours=2))

    validator = EvidenceValidator(stale_after=timedelta(hours=1))
    result = validator.validate(evidence, now=now)

    assert result.stale is True


def test_zero_stale_threshold_is_rejected() -> None:
    with pytest.raises(ValueError, match='greater than zero'):
        EvidenceValidator(stale_after=timedelta(0))


def test_naive_now_is_rejected() -> None:
    now = datetime.now(timezone.utc)
    evidence = make_evidence(retrieved_at=now)

    with pytest.raises(ValueError, match='timezone-aware'):
        EvidenceValidator().validate(evidence, now=datetime.now())

