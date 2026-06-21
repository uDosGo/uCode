"""Compatibility wrapper for legacy Sonic-facing promotion imports."""

from uhome_server.sonic import _warn_legacy_import
from uhome_server.installer.promotion import PromotionResult, RollbackResult, VerificationResult, promote_target_root, rollback_promoted_target, verify_promoted_target

_warn_legacy_import("uhome_server.sonic.promotion", "uhome_server.installer.promotion")

__all__ = [
    "PromotionResult",
    "RollbackResult",
    "VerificationResult",
    "promote_target_root",
    "rollback_promoted_target",
    "verify_promoted_target",
]
