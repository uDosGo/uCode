"""Host prerequisite checks for Ubuntu-class uHOME deployments."""

from __future__ import annotations

import os
import platform
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path


def _parse_version(value: str) -> tuple[int, ...]:
    parts: list[int] = []
    for chunk in value.replace("-", ".").split("."):
        if chunk.isdigit():
            parts.append(int(chunk))
        else:
            break
    return tuple(parts)


def _version_at_least(actual: tuple[int, ...], minimum: tuple[int, ...]) -> bool:
    width = max(len(actual), len(minimum))
    actual_padded = actual + (0,) * (width - len(actual))
    minimum_padded = minimum + (0,) * (width - len(minimum))
    return actual_padded >= minimum_padded


@dataclass(frozen=True)
class PrerequisiteCheck:
    ok: bool
    detail: str
    expected: str | None = None
    actual: str | None = None

    def to_dict(self) -> dict[str, str | bool | None]:
        return {
            "ok": self.ok,
            "detail": self.detail,
            "expected": self.expected,
            "actual": self.actual,
        }


@dataclass
class HostPrerequisiteReport:
    passed: bool
    checks: dict[str, PrerequisiteCheck] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "passed": self.passed,
            "checks": {name: check.to_dict() for name, check in self.checks.items()},
            "warnings": self.warnings,
        }


def evaluate_host_prerequisites(
    *,
    system_name: str,
    kernel_release: str,
    python_version: tuple[int, ...],
    storage_paths: list[Path],
    workspace_path: Path,
    command_paths: dict[str, str | None],
    systemd_runtime_present: bool,
) -> HostPrerequisiteReport:
    checks: dict[str, PrerequisiteCheck] = {}
    warnings: list[str] = []

    linux_ok = system_name == "Linux"
    checks["platform"] = PrerequisiteCheck(
        ok=linux_ok,
        detail="Linux host detected." if linux_ok else "uHOME-server operational deployment targets Linux hosts.",
        expected="Linux",
        actual=system_name,
    )

    kernel_version = _parse_version(kernel_release)
    kernel_minimum = (5, 4)
    kernel_ok = bool(kernel_version) and _version_at_least(kernel_version, kernel_minimum)
    checks["kernel"] = PrerequisiteCheck(
        ok=kernel_ok,
        detail="Kernel release satisfies Ubuntu 20.04+ baseline."
        if kernel_ok
        else "Kernel release is below the Ubuntu 20.04+ baseline.",
        expected=">= 5.4",
        actual=kernel_release,
    )

    python_minimum = (3, 9)
    python_ok = _version_at_least(python_version, python_minimum)
    checks["python"] = PrerequisiteCheck(
        ok=python_ok,
        detail="Python runtime is suitable for uHOME-server." if python_ok else "Python 3.9+ is required.",
        expected=">= 3.9",
        actual=".".join(str(part) for part in python_version[:3]),
    )

    systemctl_ok = bool(command_paths.get("systemctl"))
    checks["systemctl"] = PrerequisiteCheck(
        ok=systemctl_ok,
        detail="systemctl is available." if systemctl_ok else "systemctl is required for service management.",
        expected="command available",
        actual=command_paths.get("systemctl") or "missing",
    )

    systemd_ok = systemctl_ok and systemd_runtime_present
    checks["systemd_runtime"] = PrerequisiteCheck(
        ok=systemd_ok,
        detail="systemd runtime is active." if systemd_ok else "systemd runtime not detected on this host.",
        expected="/run/systemd/system present",
        actual="present" if systemd_runtime_present else "missing",
    )

    workspace_ok = workspace_path.exists() and workspace_path.is_dir()
    checks["workspace_path"] = PrerequisiteCheck(
        ok=workspace_ok,
        detail="Workspace path exists." if workspace_ok else "Workspace path is missing.",
        expected="existing directory",
        actual=str(workspace_path),
    )

    for storage_path in storage_paths:
        storage_exists = storage_path.exists() and storage_path.is_dir()
        checks[f"storage:{storage_path}"] = PrerequisiteCheck(
            ok=storage_exists,
            detail="Storage path exists." if storage_exists else "Storage path is missing.",
            expected="existing directory",
            actual=str(storage_path),
        )
        if storage_exists and not os_access_writable(storage_path):
            warnings.append(f"Storage path {storage_path} exists but is not writable by the current user.")

    for optional_command in ("curl", "jq", "journalctl"):
        if not command_paths.get(optional_command):
            warnings.append(f"Optional command '{optional_command}' not found; some operator scripts will be less useful.")

    passed = all(check.ok for check in checks.values())
    return HostPrerequisiteReport(passed=passed, checks=checks, warnings=warnings)


def os_access_writable(path: Path) -> bool:
    try:
        path.stat()
    except OSError:
        return False
    return path.exists() and path.is_dir() and os.access(path, os.W_OK)


def collect_host_prerequisites(
    *,
    storage_paths: list[str] | None = None,
    workspace_path: str | None = None,
) -> HostPrerequisiteReport:
    resolved_storage_paths = [Path(value).expanduser().resolve() for value in (storage_paths or ["/media/library"])]
    resolved_workspace_path = Path(workspace_path or "~/.workspace").expanduser().resolve()
    command_paths = {name: shutil.which(name) for name in ("systemctl", "journalctl", "curl", "jq")}
    return evaluate_host_prerequisites(
        system_name=platform.system(),
        kernel_release=platform.release(),
        python_version=tuple(sys.version_info[:3]),
        storage_paths=resolved_storage_paths,
        workspace_path=resolved_workspace_path,
        command_paths=command_paths,
        systemd_runtime_present=Path("/run/systemd/system").exists(),
    )
