"""Claude gateway domain models."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ClaudeToolDefinition:
    """Tool definition exposed to Claude."""

    name: str
    description: str
    input_schema: dict[str, Any]


@dataclass(frozen=True)
class ClaudeToolCall:
    """Tool invocation requested by Claude."""

    id: str
    name: str
    input: dict[str, Any]


@dataclass(frozen=True)
class ClaudeMessage:
    """Conversation message exchanged with Claude."""

    role: str
    content: Any


@dataclass(frozen=True)
class ClaudeRequest:
    """Input to the Claude gateway."""

    prompt: str
    system_prompt: str | None = None
    max_tokens: int = 1024
    temperature: float = 0.0
    tools: tuple[ClaudeToolDefinition, ...] = field(default_factory=tuple)
    messages: tuple[ClaudeMessage, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ClaudeUsage:
    """Token usage returned by the model."""

    input_tokens: int
    output_tokens: int


@dataclass(frozen=True)
class ClaudeResponse:
    """Normalized Claude gateway response."""

    text: str
    model: str
    usage: ClaudeUsage
    latency_ms: float
    stop_reason: str | None
    tool_calls: tuple[ClaudeToolCall, ...] = field(default_factory=tuple)
