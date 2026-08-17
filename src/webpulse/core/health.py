"""WEBPULSE application health."""

def health_check() -> dict[str, str]:
    """Return the application health status."""
    return {"status": "ok", "project": "webpulse"}
