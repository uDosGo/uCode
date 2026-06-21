"""Compatibility wrapper for legacy Sonic-facing uHOME install-plan imports."""

from uhome_server.sonic import _warn_legacy_import
from uhome_server.installer.plan import InstallPhase, UHOMEInstallOptions, UHOMEInstallPlan, UHOMEInstallStep, build_uhome_install_plan

_warn_legacy_import("uhome_server.sonic.uhome_installer", "uhome_server.installer.plan")

__all__ = [
    "InstallPhase",
    "UHOMEInstallOptions",
    "UHOMEInstallPlan",
    "UHOMEInstallStep",
    "build_uhome_install_plan",
]
