"""Live weather MCP tool for the Project 9 vertical slice."""

from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from mcp.server import MCPServer

from mcp_liveops.mcp.evidence_tools import McpEvidenceTools

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def fetch_live_weather(
    latitude: float,
    longitude: float,
) -> dict[str, Any]:
    """Fetch current weather from the public Open-Meteo API."""

    query = urlencode(
        {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,wind_speed_10m",
        }
    )

    request = Request(
        f"{OPEN_METEO_URL}?{query}",
        headers={"User-Agent": "nexus-shield/0.1"},
    )

    try:
        with urlopen(request, timeout=10) as response:
            payload = response.read().decode("utf-8")
    except (HTTPError, URLError, TimeoutError) as exc:
        raise RuntimeError(
            f"Live weather API request failed: {exc}"
        ) from exc

    data = json.loads(payload)

    if not isinstance(data, dict):
        raise RuntimeError("Live weather API returned invalid JSON.")

    current = data.get("current")

    if not isinstance(current, dict):
        raise RuntimeError(
            "Live weather API response has no current weather data."
        )

    return data


def register_live_weather_tool(
    server: MCPServer[Any],
    evidence_tools: McpEvidenceTools | None = None,
) -> None:
    """Register the live weather evidence tool."""

    evidence = evidence_tools or McpEvidenceTools()

    @server.tool()
    def live_weather(latitude: float, longitude: float) -> str:
        """Fetch live weather and normalize it as external API evidence."""

        data = fetch_live_weather(latitude, longitude)

        current = data["current"]

        content = json.dumps(
            {
                "latitude": latitude,
                "longitude": longitude,
                "temperature_2m": current.get("temperature_2m"),
                "wind_speed_10m": current.get("wind_speed_10m"),
                "time": current.get("time"),
            },
            sort_keys=True,
        )

        result = evidence.external_api(
            provider="open-meteo",
            title="Current Weather",
            content=content,
            source_name="Open-Meteo",
            endpoint=OPEN_METEO_URL,
        )

        if not result.success:
            raise ValueError(
                result.error or "Live weather evidence acquisition failed."
            )

        return result.output

