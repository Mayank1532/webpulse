"""Integrated WEBPULSE MCP server."""

from __future__ import annotations

from typing import Any

from mcp.server import MCPServer

from webpulse.mcp.server import register_core_tools


def create_integrated_server() -> MCPServer[Any]:
    """Create the integrated WEBPULSE MCP server."""

    register_core_tools()

    from webpulse.mcp.server import get_mcp_server

    return get_mcp_server()
