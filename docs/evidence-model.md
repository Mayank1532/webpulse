# NEXUS-SHIELD Evidence Model

## Purpose

Evidence is the deterministic trust boundary between retrieved information and downstream reasoning.

The system must never treat retrieved text as automatically trustworthy.

## Design Principles

1. Evidence is provenance-first.
2. Evidence is deterministic application data.
3. LLM output is untrusted input.
4. Retrieval and reranking remain separate concerns.
5. Source identity must be preserved.
6. Retrieval time must be distinguishable from publication time.
7. Supporting and conflicting evidence must be representable.
8. Validation status must be explicit.
9. Confidence must be represented separately from source reliability.
10. Missing metadata must be represented explicitly rather than fabricated.

## EvidenceRecord Contract

| Field | Purpose |
|---|---|
| evidence_id | Stable unique evidence identifier |
| claim | Atomic claim represented by the evidence |
| content | Supporting source content |
| source_name | Human-readable source identity |
| source_type | Private document, web, API, MCP, etc. |
| source_uri | Original source location where available |
| retrieval_method | How the evidence was obtained |
| retrieved_at | Time the system retrieved the evidence |
| published_at | Source publication/update time when available |
| source_reliability | Deterministic assessment of source reliability |
| confidence | Confidence in this evidence item |
| validation_status | Current validation state |
| supporting_evidence_ids | Evidence that supports this claim |
| conflicting_evidence_ids | Evidence that conflicts with this claim |

## Important Distinctions

### Source reliability
How trustworthy the source itself is considered.

### Evidence confidence
How strongly this particular evidence supports the represented claim.

### Validation status
Whether the evidence has passed the validation workflow.

These values must not be collapsed into a single score.

## Initial Source Types

- private_document
- web
- api
- mcp
- database
- user_provided

## Initial Retrieval Methods

- document_retrieval
- vector_search
- keyword_search
- hybrid_search
- reranker
- web_request
- api_request
- mcp_tool
- direct_user_input

## Initial Validation States

- unverified
- validated
- rejected
- conflicting
- stale

## Rules

- Empty claims are invalid.
- Empty evidence content is invalid.
- Confidence must remain between 0 and 1.
- Source reliability must remain between 0 and 1.
- Supporting and conflicting evidence must not contain duplicate IDs.
- An evidence item must not conflict with itself.
- retrieved_at is mandatory because provenance requires retrieval timing.
- published_at is optional because many live sources do not expose publication time.
- source_uri is optional because private/internal sources may not have URLs.
- Unknown metadata must never be invented.

## Future Extensions

The model may later support:

- source version
- content hash
- document chunk identifier
- retrieval score
- reranking score
- validation reasons
- validator identity
- conflict group identifier
- freshness score
- citation span

These are intentionally deferred until required by later phases.
