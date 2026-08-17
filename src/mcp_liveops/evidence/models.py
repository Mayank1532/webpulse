"""Deterministic evidence domain models."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class SourceType(StrEnum):
    """Origin category of evidence."""

    PRIVATE_DOCUMENT = "private_document"
    WEB = "web"
    API = "api"
    MCP = "mcp"
    DATABASE = "database"
    USER_PROVIDED = "user_provided"


class RetrievalMethod(StrEnum):
    """Method used to retrieve evidence."""

    DOCUMENT_RETRIEVAL = "document_retrieval"
    VECTOR_SEARCH = "vector_search"
    KEYWORD_SEARCH = "keyword_search"
    HYBRID_SEARCH = "hybrid_search"
    RERANKER = "reranker"
    WEB_REQUEST = "web_request"
    API_REQUEST = "api_request"
    MCP_TOOL = "mcp_tool"
    DIRECT_USER_INPUT = "direct_user_input"


class ValidationStatus(StrEnum):
    """Current validation state of evidence."""

    UNVERIFIED = "unverified"
    VALIDATED = "validated"
    REJECTED = "rejected"
    CONFLICTING = "conflicting"
    STALE = "stale"


class EvidenceRecord(BaseModel):
    """Canonical evidence record used across NEXUS-SHIELD."""

    model_config = ConfigDict(extra='forbid', frozen=True)

    evidence_id: UUID = Field(default_factory=uuid4)
    claim: str = Field(min_length=1)
    content: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    source_type: SourceType
    source_uri: str | None = None
    retrieval_method: RetrievalMethod
    retrieved_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    published_at: datetime | None = None
    source_reliability: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    validation_status: ValidationStatus = ValidationStatus.UNVERIFIED
    supporting_evidence_ids: tuple[UUID, ...] = ()
    conflicting_evidence_ids: tuple[UUID, ...] = ()

    @field_validator('claim', 'content', 'source_name')
    @classmethod
    def reject_blank_text(cls, value: str) -> str:
        """Reject whitespace-only values."""

        normalized = value.strip()
        if not normalized:
            raise ValueError("Value cannot be blank.")
        return normalized

    @model_validator(mode='after')
    def validate_evidence_relationships(self) -> EvidenceRecord:
        """Validate supporting/conflicting evidence relationships."""

        supporting = set(self.supporting_evidence_ids)
        conflicting = set(self.conflicting_evidence_ids)

        if len(supporting) != len(self.supporting_evidence_ids):
            raise ValueError("Supporting evidence IDs must be unique.")

        if len(conflicting) != len(self.conflicting_evidence_ids):
            raise ValueError("Conflicting evidence IDs must be unique.")

        if self.evidence_id in supporting:
            raise ValueError("Evidence cannot support itself.")

        if self.evidence_id in conflicting:
            raise ValueError("Evidence cannot conflict with itself.")

        if supporting.intersection(conflicting):
            raise ValueError("Evidence cannot be both supporting and conflicting.")

        return self

