"""Health handler — includes identity status."""

from handlers.identity import get_identity


def get_health() -> dict:
    """Return system health including identity status."""
    identity = get_identity()
    return {
        "status": "ok",
        "identity": {
            "initialized": identity.get("initialized", False),
            "user_id": identity.get("user_id"),
            "codeword": identity.get("codeword"),
            "install_id": identity.get("install_id"),
            "session_id": identity.get("session_id"),
            "hostname": identity.get("hostname"),
            "platform": identity.get("platform"),
        },
    }
