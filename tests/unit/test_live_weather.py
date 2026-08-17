"""Tests for the live weather acquisition path."""

from unittest.mock import MagicMock, patch

from mcp_liveops.mcp.live_weather import fetch_live_weather


def test_fetch_live_weather_parses_current_data() -> None:
    payload = (
        b'{"current":'
        b'{"temperature_2m":25.4,"wind_speed_10m":8.2,"time":"2026-08-16T10:00"}}'
    )

    response = MagicMock()
    response.read.return_value = payload

    context = MagicMock()
    context.__enter__.return_value = response
    context.__exit__.return_value = None

    with patch(
        "mcp_liveops.mcp.live_weather.urlopen",
        return_value=context,
    ):
        result = fetch_live_weather(28.6139, 77.2090)

    assert result["current"]["temperature_2m"] == 25.4
    assert result["current"]["wind_speed_10m"] == 8.2


def test_fetch_live_weather_failure_is_controlled() -> None:
    with patch(
        "mcp_liveops.mcp.live_weather.urlopen",
        side_effect=TimeoutError("timeout"),
    ):
        try:
            fetch_live_weather(28.6139, 77.2090)
        except RuntimeError as exc:
            assert "Live weather API request failed" in str(exc)
        else:
            raise AssertionError("Expected RuntimeError")

