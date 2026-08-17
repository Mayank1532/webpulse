"""WEBPULSE MCP server foundation."""

from __future__ import annotations

from mcp.server import MCPServer

from webpulse.mcp.models import ToolMetadata
from webpulse.mcp.registry import ToolRegistry

registry = ToolRegistry()

mcp = MCPServer(
    "webpulse",
    version="0.1.0",
)


def register_core_tools() -> None:
    """Register deterministic system tools exactly once."""

    if registry.contains("health_check"):
        return

    registry.register(
        ToolMetadata(
            name="health_check",
            description="Return MCP server health information.",
            category="system",
        ),
        lambda: "webpulse MCP server is healthy",
    )


register_core_tools()


@mcp.tool()
def health_check() -> str:
    """Return MCP server health information."""
    return registry.get_handler("health_check")()


def get_mcp_server() -> MCPServer:
    """Return the configured MCP server instance."""
    return mcp
