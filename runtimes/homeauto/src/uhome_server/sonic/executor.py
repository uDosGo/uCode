"""Compatibility wrapper for legacy Sonic-facing staged execution imports."""

from uhome_server.sonic import _warn_legacy_import
from uhome_server.installer.executor import ExecutionResult, execute_staged_install

_warn_legacy_import("uhome_server.sonic.executor", "uhome_server.installer.executor")

__all__ = [
    "ExecutionResult",
    "execute_staged_install",
]
