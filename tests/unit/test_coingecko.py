import httpx
import pytest

from mcp_liveops.acquisition.coingecko import (
    COINGECKO_SIMPLE_PRICE_URL,
    CoinGeckoClient,
    CoinGeckoError,
)


def make_client(
    handler: httpx.MockTransport,
) -> CoinGeckoClient:
    return CoinGeckoClient(
        client=httpx.Client(transport=handler),
    )


def test_get_prices_returns_normalized_price_data() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/v3/simple/price"
        assert request.url.params["ids"] == "bitcoin,ethereum"
        assert request.url.params["vs_currencies"] == "usd"

        return httpx.Response(
            200,
            json={
                "bitcoin": {
                    "usd": 117000.50,
                    "usd_24h_change": 2.5,
                    "last_updated_at": 1755000000,
                },
                "ethereum": {
                    "usd": 4200.25,
                    "usd_24h_change": -1.2,
                    "last_updated_at": 1755000000,
                },
            },
        )

    client = make_client(httpx.MockTransport(handler))

    results = client.get_prices(
        coin_ids=[" Bitcoin ", "ethereum"],
    )

    assert len(results) == 2
    assert results[0].coin_id == "bitcoin"
    assert results[0].currency == "usd"
    assert results[0].price == 117000.50
    assert results[0].change_24h_percent == 2.5
    assert results[1].coin_id == "ethereum"
    assert results[1].price == 4200.25
    assert results[1].change_24h_percent == -1.2


def test_get_prices_deduplicates_coin_ids() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["ids"] == "bitcoin"

        return httpx.Response(
            200,
            json={
                "bitcoin": {
                    "usd": 117000,
                },
            },
        )

    client = make_client(httpx.MockTransport(handler))

    results = client.get_prices(
        coin_ids=["bitcoin", "BITCOIN", " bitcoin "],
        include_24h_change=False,
        include_last_updated_at=False,
    )

    assert len(results) == 1
    assert results[0].coin_id == "bitcoin"


def test_get_prices_rejects_empty_coin_ids() -> None:
    client = CoinGeckoClient(
        client=httpx.Client(
            transport=httpx.MockTransport(
                lambda _: httpx.Response(200, json={})
            )
        )
    )

    with pytest.raises(ValueError, match="at least one"):
        client.get_prices(coin_ids=[])


def test_get_prices_rejects_empty_currency() -> None:
    client = CoinGeckoClient(
        client=httpx.Client(
            transport=httpx.MockTransport(
                lambda _: httpx.Response(200, json={})
            )
        )
    )

    with pytest.raises(ValueError, match="currency must not be empty"):
        client.get_prices(
            coin_ids=["bitcoin"],
            currency=" ",
        )


def test_get_prices_handles_http_failure() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(429)

    client = make_client(httpx.MockTransport(handler))

    with pytest.raises(
        CoinGeckoError,
        match="HTTP 429",
    ):
        client.get_prices(coin_ids=["bitcoin"])


def test_get_prices_handles_timeout() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timed out")

    client = make_client(httpx.MockTransport(handler))

    with pytest.raises(
        CoinGeckoError,
        match="timed out",
    ):
        client.get_prices(coin_ids=["bitcoin"])


def test_get_prices_handles_invalid_json() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            content=b"not-json",
        )

    client = make_client(httpx.MockTransport(handler))

    with pytest.raises(
        CoinGeckoError,
        match="invalid JSON",
    ):
        client.get_prices(coin_ids=["bitcoin"])


def test_get_prices_handles_missing_coin() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={},
        )

    client = make_client(httpx.MockTransport(handler))

    with pytest.raises(
        CoinGeckoError,
        match="no data for coin ID",
    ):
        client.get_prices(coin_ids=["bitcoin"])


def test_get_prices_handles_invalid_response_structure() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json=[],
        )

    client = make_client(httpx.MockTransport(handler))

    with pytest.raises(
        CoinGeckoError,
        match="unexpected response structure",
    ):
        client.get_prices(coin_ids=["bitcoin"])


def test_endpoint_constant_is_correct() -> None:
    assert (
        COINGECKO_SIMPLE_PRICE_URL
        == "https://api.coingecko.com/api/v3/simple/price"
    )
