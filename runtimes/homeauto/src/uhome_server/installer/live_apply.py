"""Run guarded Ubuntu apply plans for promoted uHOME host roots."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from uhome_server.config import utc_now_iso_z


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


@dataclass(frozen=True)
class LiveApplyResult:
    host_root: Path
    execute: bool
    ok: bool
    commands: list[dict[str, Any]]
    report_path: Path

    def to_dict(self) -> dict[str, Any]:
        return {
            "host_root": str(self.host_root),
            "execute": self.execute,
            "ok": self.ok,
            "commands": self.commands,
            "report_path": str(self.report_path),
        }


def run_ubuntu_apply_plan(
    host_root: Path,
    *,
    execute: bool = False,
    runner: Callable[..., subprocess.CompletedProcess[str]] | None = None,
) -> LiveApplyResult:
    plan_path = host_root / "var" / "lib" / "uhome" / "ubuntu-apply-plan.sh"
    if not plan_path.exists():
        raise ValueError(f"Ubuntu apply plan does not exist: {plan_path}")

    runner = runner or subprocess.run
    commands: list[dict[str, Any]] = []
    ok = True
    for raw_line in plan_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line in {"set -eu"} or line.startswith("HOST_ROOT="):
            continue
        if not execute:
            commands.append({"command": line, "executed": False, "ok": True, "status": "planned"})
            continue
        completed = runner(line, shell=True, text=True, capture_output=True)
        command_ok = completed.returncode == 0
        ok = ok and command_ok
        commands.append(
            {
                "command": line,
                "executed": True,
                "ok": command_ok,
                "returncode": completed.returncode,
                "stdout": (completed.stdout or "").strip(),
                "stderr": (completed.stderr or "").strip(),
            }
        )

    report_path = _write_json(
        host_root / "var" / "lib" / "uhome" / "ubuntu-apply-report.json",
        {
            "executed_at": utc_now_iso_z(),
            "host_root": str(host_root),
            "execute": execute,
            "ok": ok,
            "commands": commands,
        },
    )
    return LiveApplyResult(host_root=host_root, execute=execute, ok=ok, commands=commands, report_path=report_path)
