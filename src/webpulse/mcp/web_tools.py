"""MCP web retrieval tool."""

from __future__ import annotations

import json
from typing import Any

from mcp.server import MCPServer

from webpulse.acquisition import WebRetriever
from webpulse.mcp.models import ToolMetadata
from webpulse.mcp.registry import ToolRegistry

WEB_RETRIEVE_TOOL_NAME = "web_retrieve"

WEB_RETRIEVE_DESCRIPTION = (
    "Retrieve and extract readable content from a specific public web URL. "
    "Use this tool when current information from the live web is required."
)


class WebMcpTools:
    """Application boundary for controlled web retrieval."""

    def __init__(
        self,
        retriever: WebRetriever | None = None,
    ) -> None:
        """Initialize the web MCP tool adapter."""
        self._retriever = retriever or WebRetriever()

    def retrieve(self, url: str) -> str:
        """Retrieve a web page and return a structured JSON result."""

        result = self._retriever.retrieve(url)

        return json.dumps(
            result.model_dump(mode="json"),
            sort_keys=True,
        )

    def metadata(self) -> ToolMetadata:
        """Return metadata for the web retrieval MCP tool."""

        return ToolMetadata(
            name=WEB_RETRIEVE_TOOL_NAME,
            description=WEB_RETRIEVE_DESCRIPTION,
            category="web",
        )


def register_web_tools(
    server: MCPServer[Any],
    registry: ToolRegistry,
    tools: WebMcpTools | None = None,
) -> None:
    """Register the controlled web retrieval MCP tool."""

    web_tools = tools or WebMcpTools()

    if not registry.contains(WEB_RETRIEVE_TOOL_NAME):
        registry.register(
            web_tools.metadata(),
            web_tools.retrieve,
        )

    @server.tool(
        name=WEB_RETRIEVE_TOOL_NAME,
        description=WEB_RETRIEVE_DESCRIPTION,
    )
    def web_retrieve(url: str) -> str:
        """Retrieve readable content from a public web URL."""

        return registry.get_handler(
            WEB_RETRIEVE_TOOL_NAME
        )(url)
