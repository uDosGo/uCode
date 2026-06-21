"""Compatibility wrapper for legacy Sonic-facing uHOME preflight imports."""

from uhome_server.sonic import _warn_legacy_import
from uhome_server.installer.preflight import DEFAULT_PROFILE, UHOMEHardwareProfile, UHOMEPreflightResult, preflight_check

_warn_legacy_import("uhome_server.sonic.uhome_preflight", "uhome_server.installer.preflight")

__all__ = [
    "DEFAULT_PROFILE",
    "UHOMEHardwareProfile",
    "UHOMEPreflightResult",
    "preflight_check",
]
