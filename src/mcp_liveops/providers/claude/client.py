"""Claude provider abstraction."""

from __future__ import annotations

import time
from typing import Any, Protocol, cast

from anthropic import Anthropic
from anthropic.types import TextBlock

from mcp_liveops.config.settings import Settings
from mcp_liveops.providers.claude.models import (
    ClaudeRequest,
    ClaudeResponse,
    ClaudeToolCall,
    ClaudeUsage,
)


class ClaudeClient(Protocol):
    """Protocol implemented by Claude-compatible clients."""

    def create_message(self, request: ClaudeRequest) -> ClaudeResponse:
        """Generate a response from the model."""


class AnthropicClaudeClient:
    """Claude client backed by the Anthropic API."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

        api_key = settings.anthropic_api_key.get_secret_value()

        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY is not configured. "
                "Set it in the .env file before using Claude."
            )

        self._client = Anthropic(
            api_key=api_key,
            timeout=settings.claude_timeout_seconds,
        )

    def create_message(self, request: ClaudeRequest) -> ClaudeResponse:
        """Send a request to Claude and normalize the response."""

        if not request.prompt.strip():
            raise ValueError("Claude prompt cannot be empty.")

        started = time.perf_counter()

        messages: list[dict[str, object]] = []

        if request.messages:
            messages.extend(
                {
                    "role": message.role,
                    "content": message.content,
                }
                for message in request.messages
            )
        else:
            messages.append(
                {
                    "role": "user",
                    "content": request.prompt,
                }
            )

        message_kwargs: dict[str, Any] = {
            "model": self._settings.claude_model,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "system": request.system_prompt or "",
            "messages": messages,
        }

        if request.tools:
            message_kwargs["tools"] = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.input_schema,
                }
                for tool in request.tools
            ]

        message = self._client.messages.create(
            **message_kwargs,
        )

        latency_ms = (time.perf_counter() - started) * 1000

        text_parts: list[str] = []
        tool_calls: list[ClaudeToolCall] = []

        for block in message.content:
            block_type = getattr(block, "type", None)

            if block_type == "text":
                text_block = cast(TextBlock, block)
                text_parts.append(text_block.text)

            elif block_type == "tool_use":
                tool_calls.append(
                    ClaudeToolCall(
                        id=block.id,
                        name=block.name,
                        input=dict(block.input),
                    )
                )

        text = "".join(text_parts).strip()

        usage = ClaudeUsage(
            input_tokens=message.usage.input_tokens,
            output_tokens=message.usage.output_tokens,
        )

        return ClaudeResponse(
            text=text,
            model=message.model,
            usage=usage,
            latency_ms=latency_ms,
            stop_reason=message.stop_reason,
            tool_calls=tuple(tool_calls),
        )


