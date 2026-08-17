from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from mcp_liveops.evidence import (
    EvidenceRecord,
    RetrievalMethod,
    SourceType,
    ValidationStatus,
)


def make_evidence(**overrides: object) -> EvidenceRecord:
    values: dict[str, object] = {
        "claim": "The system retrieved current evidence.",
        "content": "Retrieved source content.",
        "source_name": "Example Source",
        "source_type": SourceType.WEB,
        "retrieval_method": RetrievalMethod.WEB_REQUEST,
        "retrieved_at": datetime.now(timezone.utc),
        "source_reliability": 0.8,
        "confidence": 0.9,
        "validation_status": ValidationStatus.UNVERIFIED,
    }
    values.update(overrides)
    return EvidenceRecord(**values)


def test_valid_evidence_record() -> None:
    record = make_evidence()

    assert record.claim == 'The system retrieved current evidence.'
    assert record.source_type is SourceType.WEB
    assert record.retrieval_method is RetrievalMethod.WEB_REQUEST
    assert 0.0 <= record.confidence <= 1.0
    assert 0.0 <= record.source_reliability <= 1.0


@pytest.mark.parametrize('field', ['claim', 'content', 'source_name'])
def test_blank_text_is_rejected(field: str) -> None:
    with pytest.raises(ValidationError):
        make_evidence(**{field: '   '})


@pytest.mark.parametrize(
    ('field', 'value'),
    [
        ('confidence', -0.01),
        ('confidence', 1.01),
        ('source_reliability', -0.01),
        ('source_reliability', 1.01),
    ],
)
def test_scores_must_be_between_zero_and_one(
    field: str,
    value: float,
) -> None:
    with pytest.raises(ValidationError):
        make_evidence(**{field: value})


def test_source_uri_is_optional() -> None:
    record = make_evidence(source_uri=None)

    assert record.source_uri is None


def test_published_at_is_optional() -> None:
    record = make_evidence(published_at=None)

    assert record.published_at is None


def test_duplicate_supporting_ids_are_rejected() -> None:
    evidence_id = uuid4()

    with pytest.raises(ValidationError, match='Supporting evidence IDs must be unique'):
        make_evidence(supporting_evidence_ids=(evidence_id, evidence_id))


def test_self_support_is_rejected() -> None:
    evidence_id = uuid4()

    with pytest.raises(ValidationError, match='cannot support itself'):
        make_evidence(
            evidence_id=evidence_id,
            supporting_evidence_ids=(evidence_id,),
        )


def test_self_conflict_is_rejected() -> None:
    evidence_id = uuid4()

    with pytest.raises(ValidationError, match='cannot conflict with itself'):
        make_evidence(
            evidence_id=evidence_id,
            conflicting_evidence_ids=(evidence_id,),
        )


def test_same_evidence_cannot_support_and_conflict() -> None:
    related_id = uuid4()

    with pytest.raises(
        ValidationError,
        match='both supporting and conflicting',
    ):
        make_evidence(
            supporting_evidence_ids=(related_id,),
            conflicting_evidence_ids=(related_id,),
        )


def test_extra_fields_are_rejected() -> None:
    with pytest.raises(ValidationError):
        make_evidence(unexpected_field='not allowed')


def test_evidence_record_is_immutable() -> None:
    record = make_evidence()

    with pytest.raises(ValidationError):
        record.claim = 'Changed claim'

