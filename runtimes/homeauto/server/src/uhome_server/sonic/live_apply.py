"""Compatibility wrapper for legacy Sonic-facing live-apply imports."""

from uhome_server.sonic import _warn_legacy_import
from uhome_server.installer import live_apply as _live_apply

_warn_legacy_import("uhome_server.sonic.live_apply", "uhome_server.installer.live_apply")

LiveApplyResult = _live_apply.LiveApplyResult
run_ubuntu_apply_plan = _live_apply.run_ubuntu_apply_plan
subprocess = _live_apply.subprocess

__all__ = [
    "LiveApplyResult",
    "run_ubuntu_apply_plan",
    "subprocess",
]
