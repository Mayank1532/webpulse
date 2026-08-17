"""Tests for Claude and MCP orchestration."""

from dataclasses import dataclass
from typing import Any

import pytest
from mcp.server import MCPServer

from mcp_liveops.core.agent import LiveOpsAgent
from mcp_liveops.mcp.client import McpClientAdapter
from mcp_liveops.mcp.coingecko_tools import (
    McpCoinGeckoTools,
    register_coingecko_tools,
)
from mcp_liveops.providers.claude.models import (
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


class FakeCoinGeckoClient:
    """Deterministic market-data provider."""

    def get_prices(
        self,
        *,
        coin_ids: list[str],
        currency: str = "usd",
        include_24h_change: bool = True,
        include_last_updated_at: bool = True,
    ) -> list[Any]:
        """Return deterministic market data."""

        from mcp_liveops.acquisition.coingecko import CoinPrice

        return [
            CoinPrice(
                coin_id=coin_id,
                currency=currency,
                price=100.0 + index,
                change_24h_percent=1.0,
                last_updated_at=1755000000,
            )
            for index, coin_id in enumerate(coin_ids)
        ]


def create_test_server() -> MCPServer:
    """Create a deterministic MCP server."""

    server = MCPServer(
        "mcp-liveops-agent-test",
        version="0.1.0",
    )

    register_coingecko_tools(
        server,
        McpCoinGeckoTools(FakeCoinGeckoClient()),
    )

    return server


@pytest.mark.anyio
async def test_agent_completes_two_turn_tool_loop() -> None:
    """The agent should execute the MCP tool and send its result back to Claude."""

    claude = FakeClaudeClient(
        responses=[
            ClaudeResponse(
                text="",
                model="claude-test-model",
                usage=ClaudeUsage(
                    input_tokens=10,
                    output_tokens=5,
                ),
                latency_ms=10.0,
                stop_reason="tool_use",
                tool_calls=(
                    ClaudeToolCall(
                        id="tool_1",
                        name="get_crypto_prices",
                        input={
                            "coin_ids": ["bitcoin", "ethereum"],
                            "currency": "usd",
                        },
                    ),
                ),
            ),
            ClaudeResponse(
                text="Bitcoin is $100 and Ethereum is $101.",
                model="claude-test-model",
                usage=ClaudeUsage(
                    input_tokens=30,
                    output_tokens=10,
                ),
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
        "What are the current Bitcoin and Ethereum prices?",
        create_test_server(),
    )

    assert response.text == "Bitcoin is $100 and Ethereum is $101."
    assert len(claude.requests) == 2

    second_request = claude.requests[1]

    assert len(second_request.messages) == 3
    assert second_request.messages[0].role == "user"
    assert second_request.messages[0].content == (
        "What are the current Bitcoin and Ethereum prices?"
    )

    assert second_request.messages[1].role == "assistant"
    assert second_request.messages[1].content[0]["type"] == "tool_use"
    assert second_request.messages[1].content[0]["name"] == "get_crypto_prices"

    assert second_request.messages[2].role == "user"
    assert second_request.messages[2].content[0]["type"] == "tool_result"
    assert second_request.messages[2].content[0]["tool_use_id"] == "tool_1"


@pytest.mark.anyio
async def test_agent_returns_direct_response_without_tool_call() -> None:
    """The agent should not perform a second Claude call when no tool is requested."""

    expected = ClaudeResponse(
        text="I can answer this directly.",
        model="claude-test-model",
        usage=ClaudeUsage(
            input_tokens=5,
            output_tokens=5,
        ),
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
                usage=ClaudeUsage(
                    input_tokens=10,
                    output_tokens=5,
                ),
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
                usage=ClaudeUsage(
                    input_tokens=20,
                    output_tokens=8,
                ),
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
