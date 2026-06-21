"""Run promoted host health checks from the generated plan."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from uhome_server.config import utc_now_iso_z


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return payload


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


@dataclass(frozen=True)
class HealthCheckRunResult:
    host_root: Path
    ok: bool
    checks: list[dict[str, Any]]
    report_path: Path

    def to_dict(self) -> dict[str, Any]:
        return {
            "host_root": str(self.host_root),
            "ok": self.ok,
            "checks": self.checks,
            "report_path": str(self.report_path),
        }


def run_promoted_health_checks(
    host_root: Path,
    runner: Callable[..., subprocess.CompletedProcess[str]] | None = None,
) -> HealthCheckRunResult:
    plan_path = host_root / "var" / "lib" / "uhome" / "health-check-plan.json"
    if not plan_path.exists():
        raise ValueError(f"Health check plan does not exist: {plan_path}")
    plan = _read_json(plan_path)
    checks = plan.get("checks", [])
    if not isinstance(checks, list):
        raise ValueError(f"Invalid health check plan contents: {plan_path}")

    runner = runner or subprocess.run
    results: list[dict[str, Any]] = []
    for item in checks:
        service = str(item.get("service") or "").strip()
        probe = item.get("health_check")
        if not service:
            continue
        if not isinstance(probe, dict):
            results.append({"service": service, "ok": False, "error": "missing health_check"})
            continue
        command = str(probe.get("command") or "").strip()
        if not command:
            results.append({"service": service, "ok": False, "error": "missing command", "health_check": probe})
            continue
        completed = runner(command, shell=True, text=True, capture_output=True)
        results.append(
            {
                "service": service,
                "ok": completed.returncode == 0,
                "returncode": completed.returncode,
                "stdout": (completed.stdout or "").strip(),
                "stderr": (completed.stderr or "").strip(),
                "health_check": probe,
            }
        )

    ok = all(item.get("ok", False) for item in results) if results else False
    report_path = _write_json(
        host_root / "var" / "lib" / "uhome" / "health-check-report.json",
        {
            "executed_at": utc_now_iso_z(),
            "host_root": str(host_root),
            "ok": ok,
            "checks": results,
        },
    )
    return HealthCheckRunResult(host_root=host_root, ok=ok, checks=results, report_path=report_path)
