"""Compatibility wrapper for legacy Sonic-facing Linux asset imports."""

from uhome_server.sonic import _warn_legacy_import
from uhome_server.installer.linux_assets import LinuxServiceAsset, render_environment_file, render_service_unit, service_asset

_warn_legacy_import("uhome_server.sonic.linux_assets", "uhome_server.installer.linux_assets")

__all__ = [
    "LinuxServiceAsset",
    "render_environment_file",
    "render_service_unit",
    "service_asset",
]
