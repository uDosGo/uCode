"""Migrate legacy wizard paths and manifest keys to kiosk terminology."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class WizardToKioskReport:
    ok: bool = True
    presentation: dict[str, Any] = field(default_factory=dict)
    manifests: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def _migrate_container_manifest(data: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    changed = False
    policy = data.get("policy")
    if isinstance(policy, dict) and "wizard_only" in policy:
        wo = policy.pop("wizard_only")
        changed = True
        if "thin_kiosk_only" not in policy:
            policy["thin_kiosk_only"] = wo

    def _fix_callable_from(obj: dict[str, Any], key: str) -> None:
        nonlocal changed
        raw = obj.get(key)
        if not isinstance(raw, list):
            return
        new_list: list[str] = []
        for item in raw:
            if not isinstance(item, str):
                continue
            s = item.strip()
            if s.lower() == "wizard":
                new_list.append("thin-kiosk")
                changed = True
            else:
                new_list.append(s)
        if new_list != raw:
            obj[key] = new_list
            changed = True

    meta = data.get("metadata")
    if isinstance(meta, dict):
        _fix_callable_from(meta, "callable_from")
    _fix_callable_from(data, "callable_from")

    return data, changed


def _migrate_presentation_payload(data: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    changed = False
    for lane_key in ("thin_gui", "steam_console"):
        block = data.get(lane_key)
        if not isinstance(block, dict):
            continue
        intent = block.get("intent")
        if not isinstance(intent, dict):
            continue
        auth = intent.get("auth")
        if not isinstance(auth, dict):
            continue
        if "wizard_mode_active" in auth:
            wma = auth.pop("wizard_mode_active")
            if "kiosk_local_session" not in auth:
                auth["kiosk_local_session"] = not bool(wma)
            changed = True
    return data, changed


def migrate_presentation_state(
    repo_root: Path,
    *,
    dry_run: bool,
    force: bool,
    remove_legacy: bool,
) -> dict[str, Any]:
    legacy = repo_root / "memory" / "wizard" / "uhome" / "presentation.json"
    target_dir = repo_root / "memory" / "kiosk" / "uhome"
    target = target_dir / "presentation.json"
    result: dict[str, Any] = {
        "legacy_path": str(legacy),
        "target_path": str(target),
        "action": "noop",
    }
    if not legacy.exists():
        result["action"] = "skipped_no_legacy"
        return result

    payload = json.loads(legacy.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in {legacy}")

    payload, _ = _migrate_presentation_payload(payload)

    if target.exists() and not force:
        result["action"] = "skipped_target_exists"
        result["note"] = "Use --force to overwrite kiosk presentation.json"
        return result

    if not dry_run:
        target_dir.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        result["action"] = "copied_and_rewritten"
        if remove_legacy:
            legacy.unlink()
            result["legacy_removed"] = True
    else:
        result["action"] = "dry_run_would_copy"

    return result


def migrate_library_container_manifests(
    repo_root: Path,
    *,
    dry_run: bool,
) -> list[dict[str, Any]]:
    library_root = repo_root / "library"
    reports: list[dict[str, Any]] = []
    if not library_root.is_dir():
        return reports

    for path in sorted(library_root.rglob("container.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            reports.append({"path": str(path), "ok": False, "error": str(exc)})
            continue
        if not isinstance(data, dict):
            reports.append({"path": str(path), "ok": False, "error": "not_a_json_object"})
            continue

        new_data, changed = _migrate_container_manifest(data)
        rel = str(path.relative_to(repo_root))
        if not changed:
            reports.append({"path": rel, "ok": True, "changed": False})
            continue
        if not dry_run:
            path.write_text(json.dumps(new_data, indent=2) + "\n", encoding="utf-8")
        reports.append({"path": rel, "ok": True, "changed": True, "dry_run": dry_run})

    return reports


def run_wizard_to_kiosk_migration(
    repo_root: Path,
    *,
    dry_run: bool = False,
    force: bool = False,
    remove_legacy: bool = False,
    skip_presentation: bool = False,
    skip_manifests: bool = False,
) -> WizardToKioskReport:
    report = WizardToKioskReport()
    root = repo_root.expanduser().resolve()

    if not skip_presentation:
        try:
            report.presentation = migrate_presentation_state(
                root,
                dry_run=dry_run,
                force=force,
                remove_legacy=remove_legacy,
            )
        except Exception as exc:
            report.ok = False
            report.errors.append(f"presentation: {exc}")

    if not skip_manifests:
        try:
            report.manifests = migrate_library_container_manifests(root, dry_run=dry_run)
            if any(not m.get("ok", True) for m in report.manifests):
                report.ok = False
        except Exception as exc:
            report.ok = False
            report.errors.append(f"manifests: {exc}")

    return report
