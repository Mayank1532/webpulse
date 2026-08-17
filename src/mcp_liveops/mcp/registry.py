"""MCP tool registry."""

from __future__ import annotations

from collections.abc import Callable

from mcp_liveops.mcp.models import ToolMetadata

ToolHandler = Callable[..., str]


class ToolRegistry:
    """Deterministic registry for application MCP tools."""

    def __init__(self) -> None:
        """Initialize an empty registry."""
        self._handlers: dict[str, ToolHandler] = {}
        self._metadata: dict[str, ToolMetadata] = {}

    def register(
        self,
        metadata: ToolMetadata,
        handler: ToolHandler,
    ) -> None:
        """Register a tool and reject duplicate names."""

        if metadata.name in self._handlers:
            raise ValueError(
                f"Tool already registered: {metadata.name}"
            )

        self._handlers[metadata.name] = handler
        self._metadata[metadata.name] = metadata

    def get_handler(self, name: str) -> ToolHandler:
        """Return a registered handler."""

        try:
            return self._handlers[name]
        except KeyError as exc:
            raise KeyError(f"Unknown MCP tool: {name}") from exc

    def list_metadata(self) -> list[ToolMetadata]:
        """Return registered metadata in deterministic order."""

        return [
            self._metadata[name]
            for name in sorted(self._metadata)
        ]

    def contains(self, name: str) -> bool:
        """Return whether a tool is registered."""

        return name in self._handlers

