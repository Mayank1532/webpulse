"""Claude and MCP orchestration service."""

from __future__ import annotations

import json

from mcp.server import MCPServer

from mcp_liveops.mcp.client import McpClientAdapter
from mcp_liveops.providers.claude.client import ClaudeClient
from mcp_liveops.providers.claude.models import (
    ClaudeMessage,
    ClaudeRequest,
    ClaudeResponse,
    ClaudeToolDefinition,
)


class LiveOpsAgent:
    """Coordinate Claude reasoning with MCP tool execution."""

    def __init__(
        self,
        claude_client: ClaudeClient,
        mcp_client: McpClientAdapter | None = None,
    ) -> None:
        """Initialize the agent with provider dependencies."""

        self._claude = claude_client
        self._mcp = mcp_client or McpClientAdapter()

    async def run(
        self,
        prompt: str,
        server: MCPServer,
    ) -> ClaudeResponse:
        """Run Claude, execute requested MCP tools, and obtain a final answer."""

        tools = await self._mcp.discover_tool_definitions(server)

        claude_tools = tuple(
            ClaudeToolDefinition(
                name=tool.name,
                description=tool.description,
                input_schema=tool.input_schema,
            )
            for tool in tools
        )

        first_response = self._claude.create_message(
            ClaudeRequest(
                prompt=prompt,
                tools=claude_tools,
            )
        )

        if not first_response.tool_calls:
            return first_response

        tool_results: list[dict[str, object]] = []

        for tool_call in first_response.tool_calls:
            result = await self._mcp.invoke(
                server,
                tool_call.name,
                tool_call.input,
            )

            if result.success:
                content = result.output
            else:
                content = json.dumps(
                    {
                        "error": result.error or "MCP tool execution failed.",
                    },
                    sort_keys=True,
                )

            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": tool_call.id,
                    "content": content,
                    "is_error": not result.success,
                }
            )

        assistant_content: list[dict[str, object]] = [
            {
                "type": "tool_use",
                "id": tool_call.id,
                "name": tool_call.name,
                "input": tool_call.input,
            }
            for tool_call in first_response.tool_calls
        ]

        second_response = self._claude.create_message(
            ClaudeRequest(
                prompt=prompt,
                tools=claude_tools,
                messages=(
                    ClaudeMessage(
                        role="user",
                        content=prompt,
                    ),
                    ClaudeMessage(
                        role="assistant",
                        content=assistant_content,
                    ),
                    ClaudeMessage(
                        role="user",
                        content=tool_results,
                    ),
                ),
            )
        )

        return second_response
