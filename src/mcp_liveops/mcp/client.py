"""NEXUS-SHIELD MCP client adapter."""

from __future__ import annotations

from typing import Any

from mcp import Client
from mcp.server import MCPServer

from mcp_liveops.mcp.models import (
    McpToolDefinition,
    ToolExecutionResult,
)


class McpClientAdapter:
    """Application-facing wrapper around the official MCP client."""

    async def discover_tools(
        self,
        server: MCPServer[Any],
    ) -> list[str]:
        """Discover available tool names from an MCP server."""

        tools = await self.discover_tool_definitions(server)

        return [
            tool.name
            for tool in tools
        ]

    async def discover_tool_definitions(
        self,
        server: MCPServer[Any],
    ) -> list[McpToolDefinition]:
        """Discover normalized tool definitions from an MCP server."""

        async with Client(server) as client:
            response = await client.list_tools()

            return sorted(
                [
                    McpToolDefinition(
                        name=tool.name,
                        description=tool.description or "",
                        input_schema=dict(tool.input_schema),
                    )
                    for tool in response.tools
                ],
                key=lambda tool: tool.name,
            )

    async def invoke(
        self,
        server: MCPServer[Any],
        tool_name: str,
        arguments: dict[str, object] | None = None,
    ) -> ToolExecutionResult:
        """Invoke one MCP tool and normalize its result."""

        try:
            async with Client(server) as client:
                result = await client.call_tool(
                    tool_name,
                    arguments or {},
                )

            if getattr(result, "is_error", False):
                return ToolExecutionResult(
                    tool_name=tool_name,
                    success=False,
                    output="",
                    error=f"MCP tool returned an error: {tool_name}",
                )

            output = self._extract_text(result)

            return ToolExecutionResult(
                tool_name=tool_name,
                success=True,
                output=output,
            )

        except Exception as exc:
            return ToolExecutionResult(
                tool_name=tool_name,
                success=False,
                output="",
                error=str(exc),
            )

    def _extract_text(self, result: object) -> str:
        """Extract text content from an MCP call result."""

        content = getattr(result, "content", [])

        text_parts = [
            item.text
            for item in content
            if hasattr(item, "text")
        ]

        return "\n".join(text_parts)
