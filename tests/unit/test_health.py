from webpulse.core.health import health_check


def test_health_check() -> None:
    result = health_check()

    assert result["status"] == "ok"
    assert result["project"] == "webpulse"
