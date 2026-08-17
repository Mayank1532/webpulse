"""CoinGecko live market-data acquisition."""

from __future__ import annotations

from typing import Any

import httpx
from pydantic import BaseModel, ConfigDict, Field, ValidationError

COINGECKO_SIMPLE_PRICE_URL = (
    "https://api.coingecko.com/api/v3/simple/price"
)


class CoinPrice(BaseModel):
    """Normalized price information for one cryptocurrency."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    coin_id: str = Field(min_length=1)
    currency: str = Field(min_length=1)
    price: float
    change_24h_percent: float | None = None
    last_updated_at: int | None = None


class CoinGeckoError(Exception):
    """Raised when CoinGecko acquisition fails."""


class CoinGeckoClient:
    """Small client for CoinGecko's simple price endpoint."""

    def __init__(
        self,
        *,
        timeout_seconds: float = 10.0,
        client: httpx.Client | None = None,
    ) -> None:
        """Initialize the CoinGecko client."""

        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than zero")

        self._timeout_seconds = timeout_seconds
        self._client = client

    def get_prices(
        self,
        *,
        coin_ids: list[str],
        currency: str = "usd",
        include_24h_change: bool = True,
        include_last_updated_at: bool = True,
    ) -> list[CoinPrice]:
        """Retrieve current prices for the requested CoinGecko IDs."""

        normalized_ids = self._normalize_coin_ids(coin_ids)
        normalized_currency = currency.strip().lower()

        if not normalized_ids:
            raise ValueError("coin_ids must contain at least one non-empty ID")

        if not normalized_currency:
            raise ValueError("currency must not be empty")

        params = {
            "ids": ",".join(normalized_ids),
            "vs_currencies": normalized_currency,
            "include_24hr_change": str(include_24h_change).lower(),
            "include_last_updated_at": str(
                include_last_updated_at
            ).lower(),
        }

        try:
            response = self._request(params)
            response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise CoinGeckoError(
                "CoinGecko request timed out."
            ) from exc
        except httpx.HTTPStatusError as exc:
            raise CoinGeckoError(
                f"CoinGecko returned HTTP {exc.response.status_code}."
            ) from exc
        except httpx.RequestError as exc:
            raise CoinGeckoError(
                "CoinGecko request failed."
            ) from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise CoinGeckoError(
                "CoinGecko returned invalid JSON."
            ) from exc

        return self._parse_response(
            payload,
            coin_ids=normalized_ids,
            currency=normalized_currency,
        )

    def _request(
        self,
        params: dict[str, str],
    ) -> httpx.Response:
        """Execute the HTTP request."""

        if self._client is not None:
            return self._client.get(
                COINGECKO_SIMPLE_PRICE_URL,
                params=params,
                timeout=self._timeout_seconds,
            )

        with httpx.Client(timeout=self._timeout_seconds) as client:
            return client.get(
                COINGECKO_SIMPLE_PRICE_URL,
                params=params,
            )

    def _parse_response(
        self,
        payload: Any,
        *,
        coin_ids: list[str],
        currency: str,
    ) -> list[CoinPrice]:
        """Validate and normalize a CoinGecko response."""

        if not isinstance(payload, dict):
            raise CoinGeckoError(
                "CoinGecko returned an unexpected response structure."
            )

        results: list[CoinPrice] = []

        for coin_id in coin_ids:
            raw_coin = payload.get(coin_id)

            if raw_coin is None:
                raise CoinGeckoError(
                    f"CoinGecko returned no data for coin ID: {coin_id}"
                )

            if not isinstance(raw_coin, dict):
                raise CoinGeckoError(
                    f"CoinGecko returned invalid data for coin ID: {coin_id}"
                )

            price = raw_coin.get(currency)

            if not isinstance(price, int | float):
                raise CoinGeckoError(
                    f"CoinGecko returned no valid {currency} price "
                    f"for coin ID: {coin_id}"
                )

            try:
                results.append(
                    CoinPrice(
                        coin_id=coin_id,
                        currency=currency,
                        price=float(price),
                        change_24h_percent=self._optional_float(
                            raw_coin.get(f"{currency}_24h_change")
                        ),
                        last_updated_at=self._optional_int(
                            raw_coin.get("last_updated_at")
                        ),
                    )
                )
            except ValidationError as exc:
                raise CoinGeckoError(
                    f"CoinGecko returned invalid data for coin ID: {coin_id}"
                ) from exc

        return results

    def _normalize_coin_ids(
        self,
        coin_ids: list[str],
    ) -> list[str]:
        """Normalize and deduplicate CoinGecko IDs."""

        normalized: list[str] = []

        for coin_id in coin_ids:
            value = coin_id.strip().lower()

            if value and value not in normalized:
                normalized.append(value)

        return normalized

    def _optional_float(self, value: Any) -> float | None:
        """Convert an optional numeric value to float."""

        if value is None:
            return None

        if not isinstance(value, int | float):
            raise CoinGeckoError(
                "CoinGecko returned an invalid numeric value."
            )

        return float(value)

    def _optional_int(self, value: Any) -> int | None:
        """Convert an optional timestamp to integer."""

        if value is None:
            return None

        if not isinstance(value, int):
            raise CoinGeckoError(
                "CoinGecko returned an invalid update timestamp."
            )

        return value

