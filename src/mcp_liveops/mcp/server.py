"""NEXUS-SHIELD MCP server."""

from __future__ import annotations

from mcp.server import MCPServer

from mcp_liveops.mcp.models import ToolMetadata
from mcp_liveops.mcp.registry import ToolRegistry

registry = ToolRegistry()

mcp = MCPServer(
    "nexus-shield",
    version="0.1.0",
)


def register_core_tools() -> None:
    """Register deterministic core tools exactly once."""

    if registry.contains("health_check"):
        return

    registry.register(
        ToolMetadata(
            name="health_check",
            description="Return MCP server health information.",
            category="system",
        ),
        lambda: "nexus-shield MCP server is healthy",
    )

    registry.register(
        ToolMetadata(
            name="evidence_lookup",
            description=(
                "Return a deterministic evidence lookup result "
                "for MCP integration testing."
            ),
            category="evidence",
        ),
        _evidence_lookup,
    )


def _evidence_lookup(query: str) -> str:
    """Return a deterministic evidence lookup response."""
    normalized = query.strip()

    if not normalized:
        raise ValueError("query must not be empty")

    return f"Evidence lookup prepared for query: {normalized}"


register_core_tools()


@mcp.tool()
def health_check() -> str:
    """Return MCP server health information."""
    return registry.get_handler("health_check")()


@mcp.tool()
def evidence_lookup(query: str) -> str:
    """Return a deterministic evidence lookup result."""
    return registry.get_handler("evidence_lookup")(query)


def get_mcp_server() -> MCPServer:
    """Return the configured MCP server instance."""
    return mcp

