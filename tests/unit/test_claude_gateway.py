"""Tests for the Claude gateway."""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from webpulse.config.settings import Settings
from webpulse.providers.claude.client import AnthropicClaudeClient
from webpulse.providers.claude.models import (
    ClaudeRequest,
    ClaudeToolDefinition,
)


def test_create_message_returns_text() -> None:
    settings = Settings(anthropic_api_key="test-key")

    client = AnthropicClaudeClient(settings)

    fake_message = SimpleNamespace(
        content=[
            SimpleNamespace(
                type="text",
                text="Hello from Claude.",
            )
        ],
        model="claude-test-model",
        usage=SimpleNamespace(
            input_tokens=10,
            output_tokens=20,
        ),
        stop_reason="end_turn",
    )

    client._client = MagicMock()
    client._client.messages.create.return_value = fake_message

    response = client.create_message(
        ClaudeRequest(prompt="Hello"),
    )

    assert response.text == "Hello from Claude."
    assert response.model == "claude-test-model"
    assert response.usage.input_tokens == 10
    assert response.usage.output_tokens == 20
    assert response.stop_reason == "end_turn"
    assert response.tool_calls == ()


def test_create_message_extracts_tool_use() -> None:
    settings = Settings(anthropic_api_key="test-key")

    client = AnthropicClaudeClient(settings)

    fake_message = SimpleNamespace(
        content=[
            SimpleNamespace(
                type="tool_use",
                id="tool_123",
                name="get_crypto_prices",
                input={
                    "coin_ids": ["bitcoin", "ethereum"],
                    "currency": "usd",
                },
            )
        ],
        model="claude-test-model",
        usage=SimpleNamespace(
            input_tokens=15,
            output_tokens=12,
        ),
        stop_reason="tool_use",
    )

    client._client = MagicMock()
    client._client.messages.create.return_value = fake_message

    response = client.create_message(
        ClaudeRequest(
            prompt="What are the current Bitcoin and Ethereum prices?",
            tools=(
                ClaudeToolDefinition(
                    name="get_crypto_prices",
                    description="Get live cryptocurrency prices.",
                    input_schema={
                        "type": "object",
                        "properties": {
                            "coin_ids": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "currency": {
                                "type": "string",
                            },
                        },
                        "required": ["coin_ids"],
                    },
                ),
            ),
        ),
    )

    assert response.text == ""
    assert len(response.tool_calls) == 1

    tool_call = response.tool_calls[0]

    assert tool_call.id == "tool_123"
    assert tool_call.name == "get_crypto_prices"
    assert tool_call.input == {
        "coin_ids": ["bitcoin", "ethereum"],
        "currency": "usd",
    }


def test_create_message_forwards_tool_definitions() -> None:
    settings = Settings(anthropic_api_key="test-key")

    client = AnthropicClaudeClient(settings)

    fake_message = SimpleNamespace(
        content=[
            SimpleNamespace(
                type="text",
                text="Tool definitions received.",
            )
        ],
        model="claude-test-model",
        usage=SimpleNamespace(
            input_tokens=5,
            output_tokens=5,
        ),
        stop_reason="end_turn",
    )

    client._client = MagicMock()
    client._client.messages.create.return_value = fake_message

    tool = ClaudeToolDefinition(
        name="get_crypto_prices",
        description="Get live cryptocurrency prices.",
        input_schema={
            "type": "object",
            "properties": {
                "coin_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                }
            },
            "required": ["coin_ids"],
        },
    )

    client.create_message(
        ClaudeRequest(
            prompt="Get crypto prices.",
            tools=(tool,),
        ),
    )

    kwargs = client._client.messages.create.call_args.kwargs

    assert kwargs["tools"] == [
        {
            "name": "get_crypto_prices",
            "description": "Get live cryptocurrency prices.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "coin_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                    }
                },
                "required": ["coin_ids"],
            },
        }
    ]


def test_non_text_unknown_blocks_are_ignored() -> None:
    settings = Settings(anthropic_api_key="test-key")

    client = AnthropicClaudeClient(settings)

    fake_message = SimpleNamespace(
        content=[
            SimpleNamespace(
                type="thinking",
                text="Internal reasoning.",
            ),
            SimpleNamespace(
                type="text",
                text="Final text.",
            ),
        ],
        model="claude-test-model",
        usage=SimpleNamespace(
            input_tokens=5,
            output_tokens=5,
        ),
        stop_reason="end_turn",
    )

    client._client = MagicMock()
    client._client.messages.create.return_value = fake_message

    response = client.create_message(
        ClaudeRequest(prompt="Test mixed content."),
    )

    assert response.text == "Final text."
    assert response.tool_calls == ()


def test_empty_prompt_is_rejected() -> None:
    settings = Settings(anthropic_api_key="test-key")

    client = AnthropicClaudeClient(settings)

    with pytest.raises(ValueError, match="Claude prompt cannot be empty"):
        client.create_message(
            ClaudeRequest(prompt="   "),
        )


def test_missing_api_key_is_rejected() -> None:
    settings = Settings(anthropic_api_key="")

    with pytest.raises(
        ValueError,
        match="ANTHROPIC_API_KEY is not configured",
    ):
        AnthropicClaudeClient(settings)


def test_default_request_has_no_tools() -> None:
    request = ClaudeRequest(prompt="Hello")

    assert request.tools == ()
