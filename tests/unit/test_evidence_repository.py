from datetime import datetime, timezone
from uuid import uuid4

from mcp_liveops.evidence import (
    EvidenceRecord,
    InMemoryEvidenceRepository,
    RetrievalMethod,
    SourceType,
)


def make_evidence() -> EvidenceRecord:
    return EvidenceRecord(
        claim="Repository test claim.",
        content="Repository test content.",
        source_name="Test Source",
        source_type=SourceType.PRIVATE_DOCUMENT,
        retrieval_method=RetrievalMethod.DOCUMENT_RETRIEVAL,
        retrieved_at=datetime.now(timezone.utc),
        source_reliability=0.9,
        confidence=0.9,
    )


def test_new_repository_is_empty() -> None:
    repository = InMemoryEvidenceRepository()

    assert repository.count() == 0
    assert repository.list_all() == ()


def test_add_and_get_evidence() -> None:
    repository = InMemoryEvidenceRepository()
    evidence = make_evidence()

    stored = repository.add(evidence)
    retrieved = repository.get(evidence.evidence_id)

    assert stored == evidence
    assert retrieved == evidence
    assert repository.count() == 1


def test_get_missing_evidence_returns_none() -> None:
    repository = InMemoryEvidenceRepository()

    assert repository.get(uuid4()) is None


def test_list_all_returns_stored_records() -> None:
    repository = InMemoryEvidenceRepository()
    first = make_evidence()
    second = make_evidence()

    repository.add(first)
    repository.add(second)

    assert repository.list_all() == (first, second)


def test_delete_existing_evidence() -> None:
    repository = InMemoryEvidenceRepository()
    evidence = make_evidence()
    repository.add(evidence)

    deleted = repository.delete(evidence.evidence_id)

    assert deleted is True
    assert repository.get(evidence.evidence_id) is None
    assert repository.count() == 0


def test_delete_missing_evidence_returns_false() -> None:
    repository = InMemoryEvidenceRepository()

    assert repository.delete(uuid4()) is False


def test_same_id_replaces_existing_record() -> None:
    repository = InMemoryEvidenceRepository()
    evidence = make_evidence()

    repository.add(evidence)

    replacement = evidence.model_copy(
        update={"claim": "Updated repository claim."}
    )

    repository.add(replacement)

    assert repository.count() == 1
    assert repository.get(evidence.evidence_id) == replacement


def test_repository_returns_immutable_tuple() -> None:
    repository = InMemoryEvidenceRepository()
    evidence = make_evidence()
    repository.add(evidence)

    records = repository.list_all()

    assert isinstance(records, tuple)


def test_repository_satisfies_abstraction() -> None:
    from mcp_liveops.evidence import EvidenceRepository

    repository = InMemoryEvidenceRepository()

    assert isinstance(repository, EvidenceRepository)

