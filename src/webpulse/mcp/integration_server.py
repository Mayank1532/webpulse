"""Integrated WEBPULSE MCP server."""

from __future__ import annotations

from typing import Any

from mcp.server import MCPServer

from webpulse.mcp.server import (
    get_mcp_server,
    register_core_tools,
    registry,
)
from webpulse.mcp.web_tools import register_web_tools


def create_integrated_server() -> MCPServer[Any]:
    """Create the integrated WEBPULSE MCP server."""

    register_core_tools()

    server = get_mcp_server()

    register_web_tools(
        server,
        registry,
    )

    return server
