from webpulse.config import Settings


def test_settings_can_be_constructed_without_environment_file() -> None:
    settings = Settings(
        anthropic_api_key="test-key",
        claude_model="test-model",
        claude_max_tokens=256,
    )

    assert settings.anthropic_api_key.get_secret_value() == "test-key"
    assert settings.claude_model == "test-model"
    assert settings.claude_max_tokens == 256
