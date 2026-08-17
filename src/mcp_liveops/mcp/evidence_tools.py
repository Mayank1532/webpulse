"""MCP tools backed by the NEXUS-SHIELD evidence acquisition layer."""

from __future__ import annotations

from typing import Any

from mcp.server import MCPServer
from pydantic import HttpUrl

from mcp_liveops.acquisition import (
    AcquisitionStatus,
    ExternalApiAcquirer,
    ExternalApiResponse,
    ExternalApiStatus,
    WebAcquirer,
    WebAcquisitionResult,
)
from mcp_liveops.mcp.models import ToolExecutionResult


class McpEvidenceTools:
    """Application service exposing acquisition capabilities to MCP."""

    def __init__(
        self,
        web_acquirer: WebAcquirer | None = None,
        external_api_acquirer: ExternalApiAcquirer | None = None,
    ) -> None:
        self._web_acquirer = web_acquirer or WebAcquirer()
        self._external_api_acquirer = (
            external_api_acquirer or ExternalApiAcquirer()
        )

    def web_source(
        self,
        title: str,
        content: str,
        source_name: str,
        source_uri: str,
    ) -> ToolExecutionResult:
        """Normalize one web source through the existing acquisition layer."""

        try:
            result = self._web_acquirer.acquire(
                WebAcquisitionResult(
                    url=HttpUrl(source_uri),
                    title=title,
                    content=content,
                    source_name=source_name,
                )
            )

            return ToolExecutionResult(
                tool_name="web_evidence",
                success=result.status is AcquisitionStatus.SUCCESS,
                output=result.content,
                error=(
                    None
                    if result.status is AcquisitionStatus.SUCCESS
                    else result.message
                ),
            )

        except Exception as exc:
            return ToolExecutionResult(
                tool_name="web_evidence",
                success=False,
                output="",
                error=str(exc),
            )

    def external_api(
        self,
        provider: str,
        title: str,
        content: str,
        source_name: str,
        endpoint: str,
    ) -> ToolExecutionResult:
        """Normalize one external API response."""

        try:
            response = ExternalApiResponse(
                provider=provider,
                endpoint=HttpUrl(endpoint),
                title=title,
                content=content,
                source_name=source_name,
                status=ExternalApiStatus.SUCCESS,
                message="Provider response received.",
            )

            result = self._external_api_acquirer.acquire(response)

            return ToolExecutionResult(
                tool_name="external_api_evidence",
                success=result.status is AcquisitionStatus.SUCCESS,
                output=result.content,
                error=(
                    None
                    if result.status is AcquisitionStatus.SUCCESS
                    else result.message
                ),
            )

        except Exception as exc:
            return ToolExecutionResult(
                tool_name="external_api_evidence",
                success=False,
                output="",
                error=str(exc),
            )


def register_evidence_tools(
    mcp: MCPServer[Any],
    service: McpEvidenceTools | None = None,
) -> McpEvidenceTools:
    """Register evidence acquisition tools on an MCP server."""

    evidence = service or McpEvidenceTools()

    @mcp.tool()
    def web_evidence(
        title: str,
        content: str,
        source_name: str,
        source_uri: str,
    ) -> str:
        """Normalize and acquire a web evidence source."""

        result = evidence.web_source(
            title=title,
            content=content,
            source_name=source_name,
            source_uri=source_uri,
        )

        if not result.success:
            raise ValueError(
                result.error or "Web evidence acquisition failed."
            )

        return result.output

    @mcp.tool()
    def external_api_evidence(
        provider: str,
        title: str,
        content: str,
        source_name: str,
        endpoint: str,
    ) -> str:
        """Normalize and acquire an external API evidence response."""

        result = evidence.external_api(
            provider=provider,
            title=title,
            content=content,
            source_name=source_name,
            endpoint=endpoint,
        )

        if not result.success:
            raise ValueError(
                result.error or "External API evidence acquisition failed."
            )

        return result.output

    return evidence
