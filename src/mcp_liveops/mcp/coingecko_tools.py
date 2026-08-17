"""CoinGecko MCP tool integration."""

from __future__ import annotations

import json
from typing import Protocol

from mcp.server import MCPServer

from mcp_liveops.acquisition.coingecko import CoinGeckoClient, CoinPrice


class CoinGeckoProvider(Protocol):
    """Protocol for CoinGecko market-data providers."""

    def get_prices(
        self,
        *,
        coin_ids: list[str],
        currency: str = "usd",
        include_24h_change: bool = True,
        include_last_updated_at: bool = True,
    ) -> list[CoinPrice]:
        """Return normalized cryptocurrency prices."""


class McpCoinGeckoTools:
    """Application service exposing CoinGecko through MCP."""

    def __init__(
        self,
        client: CoinGeckoProvider | None = None,
    ) -> None:
        """Initialize the CoinGecko MCP service."""

        self._client = client or CoinGeckoClient()

    def get_crypto_prices(
        self,
        *,
        coin_ids: list[str],
        currency: str = "usd",
    ) -> str:
        """Fetch and serialize cryptocurrency market data."""

        normalized_ids = [
            coin_id.strip().lower()
            for coin_id in coin_ids
            if coin_id.strip()
        ]

        if not normalized_ids:
            raise ValueError(
                "coin_ids must contain at least one non-empty ID"
            )

        normalized_currency = currency.strip().lower()

        if not normalized_currency:
            raise ValueError("currency must not be empty")

        prices = self._client.get_prices(
            coin_ids=normalized_ids,
            currency=normalized_currency,
        )

        return json.dumps(
            {
                "prices": [
                    price.model_dump(mode="json")
                    for price in prices
                ]
            },
            sort_keys=True,
        )


def register_coingecko_tools(
    server: MCPServer,
    service: McpCoinGeckoTools | None = None,
) -> McpCoinGeckoTools:
    """Register CoinGecko tools on an MCP server."""

    market_data = service or McpCoinGeckoTools()

    @server.tool()
    def get_crypto_prices(
        coin_ids: list[str],
        currency: str = "usd",
    ) -> str:
        """Get live cryptocurrency prices from CoinGecko."""

        try:
            return market_data.get_crypto_prices(
                coin_ids=coin_ids,
                currency=currency,
            )
        except Exception as exc:
            raise ValueError(
                f"Cryptocurrency price lookup failed: {exc}"
            ) from exc

    return market_data
