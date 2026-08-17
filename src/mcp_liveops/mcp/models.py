"""MCP domain models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ToolMetadata(BaseModel):
    """Application-level metadata for a registered MCP tool."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    category: str = Field(min_length=1)


class McpToolDefinition(BaseModel):
    """Normalized MCP tool definition exposed to an application client."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str = Field(min_length=1)
    description: str = ""
    input_schema: dict[str, Any] = Field(default_factory=dict)


class ToolExecutionResult(BaseModel):
    """Normalized application result from MCP tool execution."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    tool_name: str = Field(min_length=1)
    success: bool
    output: str
    error: str | None = None
