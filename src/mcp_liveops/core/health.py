"""NEXUS-SHIELD foundation smoke endpoint."""

def health_check() -> dict[str, str]:
    """Return the initial application health status."""
    return {"status": "ok", "project": "nexus-shield"}

