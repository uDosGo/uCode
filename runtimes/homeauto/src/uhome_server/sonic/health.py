"""Compatibility wrapper for legacy Sonic-facing health-check imports."""

from uhome_server.sonic import _warn_legacy_import
from uhome_server.installer import health as _health

_warn_legacy_import("uhome_server.sonic.health", "uhome_server.installer.health")

HealthCheckRunResult = _health.HealthCheckRunResult
run_promoted_health_checks = _health.run_promoted_health_checks
subprocess = _health.subprocess

__all__ = [
    "HealthCheckRunResult",
    "run_promoted_health_checks",
    "subprocess",
]
