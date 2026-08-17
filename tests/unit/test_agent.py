"""Tests for Claude and MCP orchestration."""

from dataclasses import dataclass
from typing import Any

import pytest
from mcp.server import MCPServer

from webpulse.core.agent import LiveOpsAgent
from webpulse.mcp.client import McpClientAdapter
from webpulse.providers.claude.models import (
    ClaudeResponse,
    ClaudeToolCall,
    ClaudeUsage,
)


@dataclass
class FakeClaudeClient:
    """Deterministic Claude client for orchestration tests."""

    responses: list[ClaudeResponse]
    requests: list[Any]

    def create_message(self, request: Any) -> ClaudeResponse:
        """Return the next configured Claude response."""
        self.requests.append(request)
        return self.responses.pop(0)


def create_test_server() -> MCPServer:
    """Create a deterministic MCP server for agent tests."""

    server = MCPServer(
        "webpulse-agent-test",
        version="0.1.0",
    )

    @server.tool()
    def test_lookup(query: str) -> str:
        """Return deterministic test information."""
        if not query.strip():
            raise ValueError("query must not be empty")
        return f"Retrieved information for: {query.strip()}"

    return server


@pytest.mark.anyio
async def test_agent_completes_two_turn_tool_loop() -> None:
    """The agent should execute the MCP tool and return its result to Claude."""

    claude = FakeClaudeClient(
        responses=[
            ClaudeResponse(
                text="",
                model="claude-test-model",
                usage=ClaudeUsage(input_tokens=10, output_tokens=5),
                latency_ms=10.0,
                stop_reason="tool_use",
                tool_calls=(
                    ClaudeToolCall(
                        id="tool_1",
                        name="test_lookup",
                        input={"query": "latest Python release"},
                    ),
                ),
            ),
            ClaudeResponse(
                text="The retrieved information says the latest Python release is available.",
                model="claude-test-model",
                usage=ClaudeUsage(input_tokens=30, output_tokens=10),
                latency_ms=15.0,
                stop_reason="end_turn",
            ),
        ],
        requests=[],
    )

    agent = LiveOpsAgent(
        claude_client=claude,
        mcp_client=McpClientAdapter(),
    )

    response = await agent.run(
        "What is the latest Python release?",
        create_test_server(),
    )

    assert response.text == (
        "The retrieved information says the latest Python release is available."
    )
    assert len(claude.requests) == 2

    second_request = claude.requests[1]

    assert second_request.messages[0].role == "user"
    assert second_request.messages[1].role == "assistant"
    assert second_request.messages[1].content[0]["type"] == "tool_use"
    assert second_request.messages[1].content[0]["name"] == "test_lookup"
    assert second_request.messages[2].role == "user"
    assert second_request.messages[2].content[0]["type"] == "tool_result"
    assert second_request.messages[2].content[0]["tool_use_id"] == "tool_1"


@pytest.mark.anyio
async def test_agent_returns_direct_response_without_tool_call() -> None:
    """The agent should not perform a second Claude call without a tool request."""

    expected = ClaudeResponse(
        text="I can answer this directly.",
        model="claude-test-model",
        usage=ClaudeUsage(input_tokens=5, output_tokens=5),
        latency_ms=5.0,
        stop_reason="end_turn",
    )

    claude = FakeClaudeClient(
        responses=[expected],
        requests=[],
    )

    agent = LiveOpsAgent(claude_client=claude)

    response = await agent.run(
        "Say hello.",
        create_test_server(),
    )

    assert response == expected
    assert len(claude.requests) == 1


@pytest.mark.anyio
async def test_agent_sends_mcp_failure_back_to_claude() -> None:
    """MCP failures should be represented as tool-result errors."""

    claude = FakeClaudeClient(
        responses=[
            ClaudeResponse(
                text="",
                model="claude-test-model",
                usage=ClaudeUsage(input_tokens=10, output_tokens=5),
                latency_ms=10.0,
                stop_reason="tool_use",
                tool_calls=(
                    ClaudeToolCall(
                        id="tool_1",
                        name="unknown_tool",
                        input={},
                    ),
                ),
            ),
            ClaudeResponse(
                text="I could not execute that tool.",
                model="claude-test-model",
                usage=ClaudeUsage(input_tokens=20, output_tokens=8),
                latency_ms=12.0,
                stop_reason="end_turn",
            ),
        ],
        requests=[],
    )

    agent = LiveOpsAgent(claude_client=claude)

    response = await agent.run(
        "Use an unavailable tool.",
        create_test_server(),
    )

    assert response.text == "I could not execute that tool."

    second_request = claude.requests[1]
    tool_result = second_request.messages[2].content[0]

    assert tool_result["type"] == "tool_result"
    assert tool_result["is_error"] is True
    assert tool_result["tool_use_id"] == "tool_1"
