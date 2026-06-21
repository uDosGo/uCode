"""Deprecated compatibility layer for legacy Sonic-facing uHOME imports."""

from __future__ import annotations

import warnings


def _warn_legacy_import(legacy_name: str, replacement: str) -> None:
    warnings.warn(
        f"{legacy_name} is deprecated; use {replacement} instead.",
        DeprecationWarning,
        stacklevel=2,
    )
