"""Deterministic tests for Claude/MCP orchestration."""

from __future__ import annotations

import json
from typing import Any

import pytest

from webpulse.core.agent import LiveOpsAgent
from webpulse.mcp.models import ToolExecutionResult
from webpulse.providers.claude.models import (
    ClaudeResponse,
    ClaudeToolCall,
    ClaudeUsage,
)


class FakeClaudeClient:
    """Deterministic Claude client for orchestration tests."""

    def __init__(
        self,
        responses: list[ClaudeResponse],
    ) -> None:
        self._responses = responses
        self.requests: list[Any] = []

    def create_message(self, request: Any) -> ClaudeResponse:
        """Return the next predetermined Claude response."""
        self.requests.append(request)

        if not self._responses:
            raise AssertionError("No fake Claude response remaining.")

        return self._responses.pop(0)


class FakeMcpClient:
    """Deterministic MCP client for orchestration tests."""

    def __init__(
        self,
        *,
        tool_result: ToolExecutionResult,
    ) -> None:
        self.tool_result = tool_result
        self.discovered = 0
        self.invocations: list[tuple[str, dict[str, Any]]] = []

    async def discover_tool_definitions(self, server: Any) -> tuple[Any, ...]:
        """Return a deterministic web retrieval tool definition."""

        self.discovered += 1

        class Tool:
            name = "web_retrieve"
            description = "Retrieve readable content from a public web URL."
            input_schema = {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                    }
                },
                "required": ["url"],
            }

        return (Tool(),)

    async def invoke(
        self,
        server: Any,
        name: str,
        arguments: dict[str, Any],
    ) -> ToolExecutionResult:
        """Record invocation and return the predetermined result."""

        self.invocations.append((name, arguments))
        return self.tool_result


class FakeServer:
    """Placeholder MCP server."""

    pass


def make_tool_call(
    *,
    tool_id: str = "tool-1",
    url: str = "https://example.com",
) -> ClaudeToolCall:
    """Create a deterministic Claude tool call."""

    return ClaudeToolCall(
        id=tool_id,
        name="web_retrieve",
        input={"url": url},
    )


def make_response(
    *,
    text: str = "",
    tool_calls: tuple[ClaudeToolCall, ...] = (),
) -> ClaudeResponse:
    """Create a deterministic Claude response."""

    return ClaudeResponse(
        text=text,
        model="test-model",
        usage=ClaudeUsage(
            input_tokens=0,
            output_tokens=0,
        ),
        latency_ms=0.0,
        stop_reason="tool_use" if tool_calls else "end_turn",
        tool_calls=tool_calls,
    )


@pytest.mark.asyncio
async def test_agent_executes_claude_requested_web_tool() -> None:
    claude = FakeClaudeClient(
        [
            make_response(
                tool_calls=(make_tool_call(),),
            ),
            make_response(
                text="The live result says the requested page contains current evidence.",
            ),
        ]
    )

    mcp = FakeMcpClient(
        tool_result=ToolExecutionResult(
            tool_name="web_retrieve",
            success=True,
            output=json.dumps(
                {
                    "status": "success",
                    "url": "https://example.com",
                    "title": "Example",
                    "text": "Current evidence from the live page.",
                },
                sort_keys=True,
            ),
        )
    )

    agent = LiveOpsAgent(
        claude_client=claude,
        mcp_client=mcp,
    )

    response = await agent.run(
        "What does the live page say?",
        FakeServer(),
    )

    assert response.text == (
        "The live result says the requested page contains current evidence."
    )
    assert len(claude.requests) == 2
    assert mcp.discovered == 1
    assert mcp.invocations == [
        (
            "web_retrieve",
            {"url": "https://example.com"},
        )
    ]


@pytest.mark.asyncio
async def test_agent_sends_tool_result_back_to_claude() -> None:
    claude = FakeClaudeClient(
        [
            make_response(
                tool_calls=(
                    make_tool_call(
                        tool_id="web-123",
                        url="https://example.com/news",
                    ),
                ),
            ),
            make_response(
                text="Final grounded response.",
            ),
        ]
    )

    mcp = FakeMcpClient(
        tool_result=ToolExecutionResult(
            tool_name="web_retrieve",
            success=True,
            output='{"text":"Live article evidence."}',
        )
    )

    agent = LiveOpsAgent(
        claude_client=claude,
        mcp_client=mcp,
    )

    await agent.run(
        "Find the current article information.",
        FakeServer(),
    )

    second_request = claude.requests[1]

    assert second_request.messages[-1].role == "user"

    tool_results = second_request.messages[-1].content

    assert isinstance(tool_results, list)
    assert tool_results[0]["type"] == "tool_result"
    assert tool_results[0]["tool_use_id"] == "web-123"
    assert tool_results[0]["content"] == '{"text":"Live article evidence."}'
    assert tool_results[0]["is_error"] is False


@pytest.mark.asyncio
async def test_agent_returns_mcp_failure_to_claude() -> None:
    claude = FakeClaudeClient(
        [
            make_response(
                tool_calls=(make_tool_call(),),
            ),
            make_response(
                text="I could not retrieve the requested page.",
            ),
        ]
    )

    mcp = FakeMcpClient(
        tool_result=ToolExecutionResult(
            tool_name="web_retrieve",
            success=False,
            output="",
            error="HTTP retrieval failed.",
        )
    )

    agent = LiveOpsAgent(
        claude_client=claude,
        mcp_client=mcp,
    )

    response = await agent.run(
        "Retrieve the current page.",
        FakeServer(),
    )

    assert response.text == "I could not retrieve the requested page."

    second_request = claude.requests[1]
    tool_results = second_request.messages[-1].content

    assert tool_results[0]["is_error"] is True

    error_payload = json.loads(tool_results[0]["content"])
    assert error_payload["error"] == "HTTP retrieval failed."


@pytest.mark.asyncio
async def test_agent_supports_multiple_tool_rounds() -> None:
    claude = FakeClaudeClient(
        [
            make_response(
                tool_calls=(
                    make_tool_call(
                        tool_id="tool-1",
                        url="https://example.com/one",
                    ),
                ),
            ),
            make_response(
                tool_calls=(
                    make_tool_call(
                        tool_id="tool-2",
                        url="https://example.com/two",
                    ),
                ),
            ),
            make_response(
                text="Combined live-web answer.",
            ),
        ]
    )

    mcp = FakeMcpClient(
        tool_result=ToolExecutionResult(
            tool_name="web_retrieve",
            success=True,
            output='{"text":"Retrieved evidence."}',
        )
    )

    agent = LiveOpsAgent(
        claude_client=claude,
        mcp_client=mcp,
    )

    response = await agent.run(
        "Compare the two live pages.",
        FakeServer(),
    )

    assert response.text == "Combined live-web answer."
    assert len(claude.requests) == 3
    assert mcp.invocations == [
        (
            "web_retrieve",
            {"url": "https://example.com/one"},
        ),
        (
            "web_retrieve",
            {"url": "https://example.com/two"},
        ),
    ]


@pytest.mark.asyncio
async def test_agent_does_not_invoke_mcp_when_claude_does_not_request_tool() -> None:
    claude = FakeClaudeClient(
        [
            make_response(
                text="This can be answered without live retrieval.",
            ),
        ]
    )

    mcp = FakeMcpClient(
        tool_result=ToolExecutionResult(
            tool_name="web_retrieve",
            success=True,
            output="Should not be used.",
        )
    )

    agent = LiveOpsAgent(
        claude_client=claude,
        mcp_client=mcp,
    )

    response = await agent.run(
        "Explain what a URL is.",
        FakeServer(),
    )

    assert response.text == "This can be answered without live retrieval."
    assert len(claude.requests) == 1
    assert mcp.invocations == []
