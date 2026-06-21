"""Compatibility wrapper for legacy Sonic-facing uHOME staging imports."""

from uhome_server.sonic import _warn_legacy_import
from uhome_server.installer.staging import UHOMEStagedArtifacts, stage_install_artifacts

_warn_legacy_import("uhome_server.sonic.staging", "uhome_server.installer.staging")

__all__ = [
    "UHOMEStagedArtifacts",
    "stage_install_artifacts",
]
