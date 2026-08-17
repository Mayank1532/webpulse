from __future__ import annotations

import pytest
from pydantic import ValidationError

from webpulse.mcp import (
    McpClientAdapter,
    ToolExecutionResult,
    ToolMetadata,
    ToolRegistry,
    get_mcp_server,
)


def test_tool_metadata_is_validated_and_immutable() -> None:
    metadata = ToolMetadata(
        name="test_tool",
        description="Test tool",
        category="test",
    )

    assert metadata.name == "test_tool"

    with pytest.raises(ValidationError):
        metadata.name = "changed"


def test_registry_registers_and_discovers_deterministically() -> None:
    registry = ToolRegistry()

    registry.register(
        ToolMetadata(
            name="z_tool",
            description="Z",
            category="test",
        ),
        lambda: "z",
    )

    registry.register(
        ToolMetadata(
            name="a_tool",
            description="A",
            category="test",
        ),
        lambda: "a",
    )

    assert [item.name for item in registry.list_metadata()] == [
        "a_tool",
        "z_tool",
    ]


def test_registry_rejects_duplicate_tools() -> None:
    registry = ToolRegistry()

    metadata = ToolMetadata(
        name="duplicate",
        description="Duplicate",
        category="test",
    )

    registry.register(metadata, lambda: "first")

    with pytest.raises(ValueError, match="already registered"):
        registry.register(metadata, lambda: "second")


def test_registry_rejects_unknown_tools() -> None:
    registry = ToolRegistry()

    with pytest.raises(KeyError, match="Unknown MCP tool"):
        registry.get_handler("missing")


@pytest.mark.anyio
async def test_mcp_tool_discovery() -> None:
    client = McpClientAdapter()

    tools = await client.discover_tools(get_mcp_server())

    assert tools == ["health_check"]


@pytest.mark.anyio
async def test_mcp_health_tool_invocation() -> None:
    client = McpClientAdapter()

    result = await client.invoke(
        get_mcp_server(),
        "health_check",
    )

    assert result == ToolExecutionResult(
        tool_name="health_check",
        success=True,
        output="webpulse MCP server is healthy",
    )


@pytest.mark.anyio
async def test_mcp_unknown_tool_failure() -> None:
    client = McpClientAdapter()

    result = await client.invoke(
        get_mcp_server(),
        "does_not_exist",
    )

    assert result.success is False
    assert result.error is not None
