"""Integration tests for the MCP-LIVEOPS server."""

import json

import pytest
from mcp.server import MCPServer

from mcp_liveops.acquisition.coingecko import CoinPrice
from mcp_liveops.mcp import McpClientAdapter
from mcp_liveops.mcp.coingecko_tools import (
    McpCoinGeckoTools,
    register_coingecko_tools,
)


class FakeCoinGeckoClient:
    """Deterministic provider for MCP integration tests."""

    def get_prices(
        self,
        *,
        coin_ids: list[str],
        currency: str = "usd",
        include_24h_change: bool = True,
        include_last_updated_at: bool = True,
    ) -> list[CoinPrice]:
        """Return deterministic cryptocurrency data."""

        return [
            CoinPrice(
                coin_id=coin_id,
                currency=currency,
                price=100.0 + index,
                change_24h_percent=1.5,
                last_updated_at=1755000000,
            )
            for index, coin_id in enumerate(coin_ids)
        ]


def create_test_server() -> MCPServer:
    """Create an integrated MCP server with a fake provider."""

    server = MCPServer(
        "mcp-liveops-test",
        version="0.1.0",
    )

    service = McpCoinGeckoTools(
        FakeCoinGeckoClient(),
    )

    register_coingecko_tools(
        server,
        service,
    )

    return server


@pytest.mark.anyio
async def test_integrated_mcp_discovers_crypto_tool() -> None:
    """The integrated server should expose the crypto tool."""

    client = McpClientAdapter()

    tools = await client.discover_tools(
        create_test_server(),
    )

    assert tools == ["get_crypto_prices"]


@pytest.mark.anyio
async def test_integrated_mcp_invokes_crypto_tool() -> None:
    """The integrated server should invoke the crypto tool."""

    client = McpClientAdapter()

    result = await client.invoke(
        create_test_server(),
        "get_crypto_prices",
        {
            "coin_ids": ["bitcoin", "ethereum"],
            "currency": "usd",
        },
    )

    assert result.success is True
    assert result.error is None

    payload = json.loads(result.output)

    assert len(payload["prices"]) == 2
    assert payload["prices"][0]["coin_id"] == "bitcoin"
    assert payload["prices"][0]["price"] == 100.0
    assert payload["prices"][1]["coin_id"] == "ethereum"
    assert payload["prices"][1]["price"] == 101.0


@pytest.mark.anyio
async def test_integrated_mcp_rejects_unknown_tool() -> None:
    """The client should normalize unknown-tool failures."""

    client = McpClientAdapter()

    result = await client.invoke(
        create_test_server(),
        "unknown_tool",
        {},
    )

    assert result.success is False
    assert result.output == ""
    assert result.error


@pytest.mark.anyio
async def test_integrated_mcp_requires_valid_tool_arguments() -> None:
    """Invalid MCP arguments should result in a failed invocation."""

    client = McpClientAdapter()

    result = await client.invoke(
        create_test_server(),
        "get_crypto_prices",
        {
            "coin_ids": [],
            "currency": "usd",
        },
    )

    assert result.success is False
    assert result.output == ""
    assert result.error
