"""CLI entrypoints for uHOME launchers and installers."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from uhome_server.backup import create_backup, list_backups, restore_backup
from uhome_server.config import (
    get_repo_root,
    get_sync_record_contract_path,
    get_sync_record_schema_path,
    load_sync_record_contract,
    load_sync_record_schema,
)
from uhome_server.installer.bundle import read_bundle_manifest, verify_bundle
from uhome_server.installer.executor import execute_staged_install
from uhome_server.installer.health import run_promoted_health_checks
from uhome_server.installer.live_apply import run_ubuntu_apply_plan
from uhome_server.installer.plan import UHOMEInstallOptions, build_uhome_install_plan
from uhome_server.installer.preflight import get_host_profile, preflight_check
from uhome_server.installer.prerequisites import collect_host_prerequisites
from uhome_server.installer.promotion import (
    promote_target_root,
    rollback_promoted_target,
    verify_promoted_target,
)
from uhome_server.installer.staging import stage_install_artifacts
from uhome_server.migrations.wizard_to_kiosk import run_wizard_to_kiosk_migration
from uhome_server.services.uhome_presentation_service import (
    get_uhome_presentation_service,
)
from uhome_server.sync_records import (
    load_sync_record_envelope,
    validation_error_payload,
)
from pydantic import ValidationError


def _read_json(path: str) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return data


def _write_output(payload: dict[str, Any], out_path: str | None = None) -> None:
    rendered = json.dumps(payload, indent=2)
    if out_path:
        target = Path(out_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered + "\n", encoding="utf-8")
        return
    print(rendered)


def _launcher_repo_root(value: str | None) -> Path:
    return Path(value).expanduser().resolve() if value else get_repo_root()


def launcher_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="uhome-launcher", description="Manage local uHOME presentation launchers.")
    parser.add_argument("--repo-root", help="Override the repository root for state and workspace access.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("status", help="Show current launcher status.")
    subparsers.add_parser("menu", help="Show console action menu for launcher and stream controls.")

    start_parser = subparsers.add_parser("start", help="Start a launcher presentation.")
    start_parser.add_argument("--presentation", default="", help="Presentation to start: thin-gui or steam-console.")

    subparsers.add_parser("stop", help="Stop the active launcher presentation.")

    args = parser.parse_args(argv)
    service = get_uhome_presentation_service(repo_root=_launcher_repo_root(args.repo_root))

    if args.command == "status":
        _write_output(service.get_status())
        return 0
    if args.command == "menu":
        _write_output(service.get_console_menu())
        return 0
    if args.command == "start":
        try:
            _write_output(service.start(args.presentation))
            return 0
        except ValueError as exc:
            _write_output({"success": False, "error": str(exc)})
            return 2
    if args.command == "stop":
        _write_output(service.stop())
        return 0
    parser.error(f"Unsupported launcher command: {args.command}")
    return 2


def installer_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="uhome-installer", description="Build and inspect uHOME install plans.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    preflight_parser = subparsers.add_parser("preflight", help="Run hardware preflight against a JSON probe.")
    preflight_parser.add_argument("--probe", required=True, help="Path to a hardware probe JSON object.")
    preflight_parser.add_argument(
        "--host-profile",
        choices=["standalone-linux", "dual-boot-steam-node"],
        help="Optional named host profile to validate against.",
    )
    preflight_parser.add_argument("--output", help="Optional path to write the JSON result.")

    verify_parser = subparsers.add_parser("verify-bundle", help="Verify bundle artifacts against the manifest.")
    verify_parser.add_argument("--bundle-dir", required=True, help="Directory containing uhome-bundle.json.")
    verify_parser.add_argument("--output", help="Optional path to write the JSON result.")

    plan_parser = subparsers.add_parser("plan", help="Build a uHOME install plan from a bundle and hardware probe.")
    plan_parser.add_argument("--bundle-dir", required=True, help="Directory containing uhome-bundle.json.")
    plan_parser.add_argument("--probe", required=True, help="Path to a hardware probe JSON object.")
    plan_parser.add_argument("--install-root", default="/opt/uhome", help="Install root used for the generated plan.")
    plan_parser.add_argument("--kiosk-user", default="uhome", help="Autologin kiosk user.")
    plan_parser.add_argument("--enable-ha-bridge", action="store_true", help="Enable Home Assistant bridge config steps.")
    plan_parser.add_argument(
        "--disable-autologin-kiosk",
        action="store_true",
        help="Skip kiosk autologin enablement steps.",
    )
    plan_parser.add_argument("--dry-run", action="store_true", help="Mark the plan as a dry run.")
    plan_parser.add_argument("--output", help="Optional path to write the JSON result.")

    stage_parser = subparsers.add_parser("stage", help="Materialize a staged installer directory.")
    stage_parser.add_argument("--bundle-dir", required=True, help="Directory containing uhome-bundle.json.")
    stage_parser.add_argument("--probe", required=True, help="Path to a hardware probe JSON object.")
    stage_parser.add_argument("--stage-dir", required=True, help="Output directory for staged artifacts.")
    stage_parser.add_argument("--install-root", default="/opt/uhome", help="Install root used for the staged artifacts.")
    stage_parser.add_argument("--kiosk-user", default="uhome", help="Autologin kiosk user.")
    stage_parser.add_argument("--enable-ha-bridge", action="store_true", help="Enable Home Assistant bridge config artifacts.")
    stage_parser.add_argument(
        "--disable-autologin-kiosk",
        action="store_true",
        help="Skip kiosk autologin enablement artifacts.",
    )
    stage_parser.add_argument("--dry-run", action="store_true", help="Mark the generated plan as a dry run.")
    stage_parser.add_argument("--output", help="Optional path to write the JSON result.")

    execute_parser = subparsers.add_parser("execute-stage", help="Apply a staged installer directory into a target root.")
    execute_parser.add_argument("--stage-dir", required=True, help="Staged installer directory produced by the stage command.")
    execute_parser.add_argument("--target-root", required=True, help="Target root for applied installer artifacts.")
    execute_parser.add_argument("--output", help="Optional path to write the JSON result.")

    apply_parser = subparsers.add_parser("apply-target", help="Promote an executed target root into a host-style filesystem root.")
    apply_parser.add_argument("--target-root", required=True, help="Executed target root produced by execute-stage.")
    apply_parser.add_argument("--host-root", required=True, help="Destination host-style root.")
    apply_parser.add_argument("--output", help="Optional path to write the JSON result.")

    rollback_parser = subparsers.add_parser("rollback-target", help="Restore the latest promoted snapshot onto a host-style root.")
    rollback_parser.add_argument("--host-root", required=True, help="Host-style root that has a promotion snapshot.")
    rollback_parser.add_argument("--output", help="Optional path to write the JSON result.")

    verify_target_parser = subparsers.add_parser("verify-target", help="Verify promoted host assets under a host-style root.")
    verify_target_parser.add_argument("--host-root", required=True, help="Host-style root to verify.")
    verify_target_parser.add_argument("--output", help="Optional path to write the JSON result.")

    health_target_parser = subparsers.add_parser("health-check-target", help="Run promoted host health checks from the generated plan.")
    health_target_parser.add_argument("--host-root", required=True, help="Host-style root to health-check.")
    health_target_parser.add_argument("--output", help="Optional path to write the JSON result.")

    prereq_parser = subparsers.add_parser("check-prereqs", help="Check Ubuntu-class host prerequisites for uHOME-server.")
    prereq_parser.add_argument(
        "--storage-path",
        action="append",
        dest="storage_paths",
        help="Required storage path. Repeat the flag to check multiple paths.",
    )
    prereq_parser.add_argument(
        "--workspace-path",
        default="~/.workspace",
        help="Required workspace directory (default: ~/.workspace).",
    )
    prereq_parser.add_argument("--output", help="Optional path to write the JSON result.")

    live_apply_parser = subparsers.add_parser("apply-live", help="Run the generated Ubuntu apply plan. Dry-run unless --execute is set.")
    live_apply_parser.add_argument("--host-root", required=True, help="Host-style root containing ubuntu-apply-plan.sh.")
    live_apply_parser.add_argument("--execute", action="store_true", help="Actually execute the plan commands instead of reporting them.")
    live_apply_parser.add_argument("--output", help="Optional path to write the JSON result.")

    args = parser.parse_args(argv)

    if args.command == "preflight":
        result = preflight_check(_read_json(args.probe), host_profile=get_host_profile(args.host_profile))
        _write_output(result.to_dict(), args.output)
        return 0 if result.passed else 1

    if args.command == "verify-bundle":
        bundle_dir = Path(args.bundle_dir).expanduser().resolve()
        manifest = read_bundle_manifest(bundle_dir)
        if manifest is None:
            _write_output({"valid": False, "missing": ["uhome-bundle.json"], "corrupt": [], "warnings": []}, args.output)
            return 1
        result = verify_bundle(manifest, bundle_dir)
        _write_output(
            {"valid": result.valid, "missing": result.missing, "corrupt": result.corrupt, "warnings": result.warnings},
            args.output,
        )
        return 0 if result.valid else 1

    if args.command == "plan":
        bundle_dir = Path(args.bundle_dir).expanduser().resolve()
        opts = UHOMEInstallOptions(
            install_root=args.install_root,
            enable_autologin_kiosk=not args.disable_autologin_kiosk,
            kiosk_user=args.kiosk_user,
            enable_ha_bridge=args.enable_ha_bridge,
            dry_run=args.dry_run,
        )
        plan = build_uhome_install_plan(bundle_dir, _read_json(args.probe), opts)
        _write_output(plan.to_dict(), args.output)
        return 0 if plan.ready else 1

    if args.command == "stage":
        bundle_dir = Path(args.bundle_dir).expanduser().resolve()
        opts = UHOMEInstallOptions(
            install_root=args.install_root,
            enable_autologin_kiosk=not args.disable_autologin_kiosk,
            kiosk_user=args.kiosk_user,
            enable_ha_bridge=args.enable_ha_bridge,
            dry_run=args.dry_run,
        )
        try:
            plan, staged = stage_install_artifacts(
                bundle_dir,
                Path(args.stage_dir).expanduser().resolve(),
                _read_json(args.probe),
                opts,
            )
        except ValueError as exc:
            _write_output({"ready": False, "error": str(exc)}, args.output)
            return 1
        _write_output({"ready": plan.ready, "plan": plan.to_dict(), "staged": staged.to_dict()}, args.output)
        return 0

    if args.command == "execute-stage":
        try:
            result = execute_staged_install(
                Path(args.stage_dir).expanduser().resolve(),
                Path(args.target_root).expanduser().resolve(),
            )
        except ValueError as exc:
            _write_output({"success": False, "error": str(exc)}, args.output)
            return 1
        _write_output({"success": True, "result": result.to_dict()}, args.output)
        return 0

    if args.command == "apply-target":
        try:
            result = promote_target_root(
                Path(args.target_root).expanduser().resolve(),
                Path(args.host_root).expanduser().resolve(),
            )
        except ValueError as exc:
            _write_output({"success": False, "error": str(exc)}, args.output)
            return 1
        _write_output({"success": True, "result": result.to_dict()}, args.output)
        return 0

    if args.command == "rollback-target":
        try:
            result = rollback_promoted_target(Path(args.host_root).expanduser().resolve())
        except ValueError as exc:
            _write_output({"success": False, "error": str(exc)}, args.output)
            return 1
        _write_output({"success": True, "result": result.to_dict()}, args.output)
        return 0

    if args.command == "verify-target":
        try:
            result = verify_promoted_target(Path(args.host_root).expanduser().resolve())
        except ValueError as exc:
            _write_output({"success": False, "error": str(exc)}, args.output)
            return 1
        _write_output({"success": result.ok, "result": result.to_dict()}, args.output)
        return 0 if result.ok else 1

    if args.command == "health-check-target":
        try:
            result = run_promoted_health_checks(Path(args.host_root).expanduser().resolve())
        except ValueError as exc:
            _write_output({"success": False, "error": str(exc)}, args.output)
            return 1
        _write_output({"success": result.ok, "result": result.to_dict()}, args.output)
        return 0 if result.ok else 1

    if args.command == "check-prereqs":
        result = collect_host_prerequisites(
            storage_paths=args.storage_paths,
            workspace_path=args.workspace_path,
        )
        _write_output(result.to_dict(), args.output)
        return 0 if result.passed else 1

    if args.command == "apply-live":
        try:
            result = run_ubuntu_apply_plan(
                Path(args.host_root).expanduser().resolve(),
                execute=args.execute,
            )
        except ValueError as exc:
            _write_output({"success": False, "error": str(exc)}, args.output)
            return 1
        _write_output({"success": result.ok, "result": result.to_dict()}, args.output)
        return 0 if result.ok else 1

    parser.error(f"Unsupported installer command: {args.command}")
    return 2


def backup_main(argv: list[str] | None = None) -> int:
    """CLI for backup and restore operations."""
    parser = argparse.ArgumentParser(prog="uhome-backup", description="Backup and restore uHOME Server state.")
    parser.add_argument("--repo-root", help="Override the repository root.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Create backup command
    create_parser = subparsers.add_parser("create", help="Create a new backup.")
    create_parser.add_argument("--backup-dir", help="Directory to store backups (default: repo_root/backups).")
    create_parser.add_argument(
        "--no-workspace",
        action="store_true",
        help="Exclude workspace settings from backup.",
    )
    create_parser.add_argument("--output", help="Optional path to write JSON result.")

    # List backups command
    list_parser = subparsers.add_parser("list", help="List available backups.")
    list_parser.add_argument("--backup-dir", help="Directory containing backups (default: repo_root/backups).")
    list_parser.add_argument("--output", help="Optional path to write JSON result.")

    # Restore backup command
    restore_parser = subparsers.add_parser("restore", help="Restore from a backup.")
    restore_parser.add_argument("--backup-path", required=True, help="Path to backup directory.")
    restore_parser.add_argument("--dry-run", action="store_true", help="Validate backup without restoring.")
    restore_parser.add_argument("--output", help="Optional path to write JSON result.")

    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).expanduser().resolve() if args.repo_root else get_repo_root()

    if args.command == "create":
        backup_dir = Path(args.backup_dir).expanduser().resolve() if args.backup_dir else None
        result = create_backup(
            repo_root=repo_root,
            backup_dir=backup_dir,
            include_workspace=not args.no_workspace,
        )
        _write_output(result.to_dict(), args.output)
        return 0 if result.success else 1

    if args.command == "list":
        backup_dir = Path(args.backup_dir).expanduser().resolve() if args.backup_dir else repo_root / "backups"
        backups = list_backups(backup_dir)
        _write_output({"backups": backups, "count": len(backups)}, args.output)
        return 0

    if args.command == "restore":
        backup_path = Path(args.backup_path).expanduser().resolve()
        result = restore_backup(
            backup_path=backup_path,
            repo_root=repo_root,
            dry_run=args.dry_run,
        )
        _write_output(result.to_dict(), args.output)
        return 0 if result.success else 1

    parser.error(f"Unsupported backup command: {args.command}")
    return 2


def contracts_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="uhome-contracts", description="Inspect shared contract assets.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    sync_parser = subparsers.add_parser("sync-record", help="Show the uHOME-bundled sync-record contract metadata.")
    sync_parser.add_argument("--output", help="Optional path to write JSON result.")
    validate_parser = subparsers.add_parser("validate-sync-record", help="Validate a sync-record envelope JSON file.")
    validate_parser.add_argument("--input", required=True, help="Path to the sync-record envelope JSON file.")
    validate_parser.add_argument("--output", help="Optional path to write JSON result.")

    args = parser.parse_args(argv)

    if args.command == "sync-record":
        contract = load_sync_record_contract()
        schema = load_sync_record_schema()
        payload = {
            "contract_path": str(get_sync_record_contract_path()),
            "schema_path": str(get_sync_record_schema_path()),
            "version": contract.get("version"),
            "owner": contract.get("owner"),
            "schema_title": schema.get("title"),
            "record_types": [record["key"] for record in contract.get("record_types", [])],
        }
        _write_output(payload, args.output)
        return 0

    if args.command == "validate-sync-record":
        try:
            envelope = load_sync_record_envelope(args.input)
        except ValidationError as exc:
            _write_output(validation_error_payload(exc), args.output)
            return 1
        payload = {
            "ok": True,
            "contract_version": envelope.contract_version,
            "counts": {
                "contacts": len(envelope.contacts),
                "activities": len(envelope.activities),
                "binders": len(envelope.binders),
                "sync_metadata": len(envelope.sync_metadata),
            },
        }
        _write_output(payload, args.output)
        return 0

    parser.error(f"Unsupported contracts command: {args.command}")
    return 2


def migrate_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="uhome-migrate", description="uHOME data and layout migrations.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    w2k = subparsers.add_parser(
        "wizard-to-kiosk",
        help="Copy memory/wizard/uhome/presentation.json to memory/kiosk/uhome/ and update library container.json keys.",
    )
    w2k.add_argument("--repo-root", help="Repository root (default: installed uHOME-server repo).")
    w2k.add_argument("--dry-run", action="store_true", help="Print actions without writing files.")
    w2k.add_argument("--force", action="store_true", help="Overwrite memory/kiosk/uhome/presentation.json if it exists.")
    w2k.add_argument(
        "--remove-legacy",
        action="store_true",
        help="After a successful copy, delete the legacy wizard presentation.json.",
    )
    w2k.add_argument("--skip-presentation", action="store_true", help="Only process library/**/container.json files.")
    w2k.add_argument("--skip-manifests", action="store_true", help="Only process presentation state.")
    w2k.add_argument("--output", help="Optional path to write JSON result.")

    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).expanduser().resolve() if args.repo_root else get_repo_root()

    if args.command == "wizard-to-kiosk":
        report = run_wizard_to_kiosk_migration(
            repo_root,
            dry_run=args.dry_run,
            force=args.force,
            remove_legacy=args.remove_legacy,
            skip_presentation=args.skip_presentation,
            skip_manifests=args.skip_manifests,
        )
        payload = {
            "ok": report.ok,
            "presentation": report.presentation,
            "manifests": report.manifests,
            "errors": report.errors,
        }
        _write_output(payload, args.output)
        return 0 if report.ok else 1

    parser.error(f"Unsupported migrate command: {args.command}")
    return 2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="uhome", description="uHOME operator CLI.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("launcher", help="Manage local launcher state.")
    subparsers.add_parser("installer", help="Manage install plans and preflight.")
    subparsers.add_parser("backup", help="Backup and restore server state.")
    subparsers.add_parser("contracts", help="Inspect shared contract assets.")
    subparsers.add_parser("migrate", help="Run data layout migrations.")
    args, remaining = parser.parse_known_args(argv)
    if args.command == "launcher":
        return launcher_main(remaining)
    if args.command == "installer":
        return installer_main(remaining)
    if args.command == "backup":
        return backup_main(remaining)
    if args.command == "contracts":
        return contracts_main(remaining)
    if args.command == "migrate":
        return migrate_main(remaining)
    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
