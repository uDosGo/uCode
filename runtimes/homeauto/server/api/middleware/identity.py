"""Identity middleware — validates identity on incoming requests.

Adds identity context to requests and validates that the identity
system has been initialized before allowing certain operations.
"""

from handlers.identity import get_identity


def require_identity() -> dict:
    """Require identity to be initialized.

    Returns:
        dict with identity data if initialized, or error dict.
    """
    identity = get_identity()
    if not identity.get("initialized"):
        return {
            "error": "Identity not initialized. Run: udev init",
            "identity_required": True,
        }
    return identity


def get_identity_context() -> dict:
    """Get identity context for request processing.

    Returns identity data without requiring initialization.
    Returns empty context if Snackbar is unreachable.
    """
    try:
        identity = get_identity()
        return {
            "user_id": identity.get("user_id"),
            "codeword": identity.get("codeword"),
            "install_id": identity.get("install_id"),
            "session_id": identity.get("session_id"),
        }
    except Exception:
        return {
            "user_id": None,
            "codeword": None,
            "install_id": None,
            "session_id": None,
        }
