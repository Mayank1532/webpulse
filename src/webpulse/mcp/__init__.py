"""MCP integration package."""

from webpulse.mcp.client import McpClientAdapter
from webpulse.mcp.integration_server import create_integrated_server
from webpulse.mcp.models import (
    McpToolDefinition,
    ToolExecutionResult,
    ToolMetadata,
)
from webpulse.mcp.registry import ToolRegistry
from webpulse.mcp.server import get_mcp_server

__all__ = [
    "McpClientAdapter",
    "McpToolDefinition",
    "ToolExecutionResult",
    "ToolMetadata",
    "ToolRegistry",
    "create_integrated_server",
    "get_mcp_server",
]
