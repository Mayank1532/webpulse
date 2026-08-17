"""Tests for the CoinGecko MCP tool integration."""

import json

import pytest
from mcp.server import MCPServer

from mcp_liveops.acquisition.coingecko import CoinPrice
from mcp_liveops.mcp.coingecko_tools import (
    McpCoinGeckoTools,
    register_coingecko_tools,
)


class FakeCoinGeckoClient:
    """Deterministic CoinGecko provider for MCP tests."""

    def __init__(self) -> None:
        self.calls: list[tuple[list[str], str]] = []

    def get_prices(
        self,
        *,
        coin_ids: list[str],
        currency: str = "usd",
        include_24h_change: bool = True,
        include_last_updated_at: bool = True,
    ) -> list[CoinPrice]:
        self.calls.append((coin_ids, currency))

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


def test_service_returns_structured_json() -> None:
    client = FakeCoinGeckoClient()
    service = McpCoinGeckoTools(client)

    output = service.get_crypto_prices(
        coin_ids=["bitcoin", "ethereum"],
    )

    payload = json.loads(output)

    assert len(payload["prices"]) == 2
    assert payload["prices"][0]["coin_id"] == "bitcoin"
    assert payload["prices"][0]["currency"] == "usd"
    assert payload["prices"][0]["price"] == 100.0
    assert client.calls == [
        (["bitcoin", "ethereum"], "usd"),
    ]


def test_service_passes_currency_to_provider() -> None:
    client = FakeCoinGeckoClient()
    service = McpCoinGeckoTools(client)

    output = service.get_crypto_prices(
        coin_ids=["bitcoin"],
        currency="eur",
    )

    payload = json.loads(output)

    assert payload["prices"][0]["currency"] == "eur"
    assert client.calls == [
        (["bitcoin"], "eur"),
    ]


def test_tool_registration_exposes_get_crypto_prices() -> None:
    server = MCPServer(
        "mcp-liveops-test",
        version="0.1.0",
    )

    register_coingecko_tools(
        server,
        FakeCoinGeckoClient(),
    )

    assert server is not None


def test_service_propagates_provider_errors() -> None:
    class FailingClient:
        def get_prices(
            self,
            *,
            coin_ids: list[str],
            currency: str = "usd",
            include_24h_change: bool = True,
            include_last_updated_at: bool = True,
        ) -> list[CoinPrice]:
            raise RuntimeError("provider unavailable")

    service = McpCoinGeckoTools(FailingClient())

    with pytest.raises(RuntimeError, match="provider unavailable"):
        service.get_crypto_prices(
            coin_ids=["bitcoin"],
        )
