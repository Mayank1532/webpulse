"""Integrated MCP-LIVEOPS server."""

from __future__ import annotations

from typing import Any

from mcp.server import MCPServer

from mcp_liveops.mcp.coingecko_tools import register_coingecko_tools


def create_integrated_server() -> MCPServer[Any]:
    """Create the MCP-LIVEOPS integrated server."""

    server = MCPServer(
        "mcp-liveops",
        version="0.1.0",
    )

    register_coingecko_tools(server)

    return server
