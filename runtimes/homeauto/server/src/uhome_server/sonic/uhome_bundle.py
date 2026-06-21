"""Compatibility wrapper for legacy Sonic-facing uHOME bundle imports."""

from uhome_server.sonic import _warn_legacy_import
from uhome_server.installer.bundle import (
    BUNDLE_MANIFEST_FILENAME,
    BUNDLE_SCHEMA_VERSION,
    ROLLBACK_FILENAME,
    UHOME_COMPONENT_IDS,
    BundleVerifyResult,
    UHOMEBundleComponent,
    UHOMEBundleManifest,
    UHOMERollbackRecord,
    compute_checksum,
    read_bundle_manifest,
    read_rollback_record,
    verify_bundle,
    verify_checksum,
    write_bundle_manifest,
    write_rollback_record,
)

_warn_legacy_import("uhome_server.sonic.uhome_bundle", "uhome_server.installer.bundle")

__all__ = [
    "BUNDLE_MANIFEST_FILENAME",
    "BUNDLE_SCHEMA_VERSION",
    "ROLLBACK_FILENAME",
    "UHOME_COMPONENT_IDS",
    "BundleVerifyResult",
    "UHOMEBundleComponent",
    "UHOMEBundleManifest",
    "UHOMERollbackRecord",
    "compute_checksum",
    "read_bundle_manifest",
    "read_rollback_record",
    "verify_bundle",
    "verify_checksum",
    "write_bundle_manifest",
    "write_rollback_record",
]
