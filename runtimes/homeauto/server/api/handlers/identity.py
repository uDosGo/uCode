"""Identity handler — proxies to Snackbar /v1/identity."""

import json
import urllib.request
from typing import Optional


SNACKBAR_IDENTITY_URL = "http://localhost:8484/v1/identity"


def get_identity() -> dict:
    """Fetch identity from Snackbar.

    Returns:
        dict with user_id, codeword, install_id, session_id,
        hostname, platform, initialized
    """
    try:
        req = urllib.request.Request(
            SNACKBAR_IDENTITY_URL,
            method="GET",
            headers={"Accept": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {
            "error": f"Snackbar unreachable: {e}",
            "user_id": None,
            "codeword": None,
            "install_id": None,
            "session_id": None,
            "hostname": None,
            "platform": None,
            "initialized": False,
        }
