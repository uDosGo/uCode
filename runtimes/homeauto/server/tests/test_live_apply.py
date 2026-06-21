from __future__ import annotations

from pathlib import Path

from uhome_server.installer.live_apply import run_ubuntu_apply_plan


def _write_plan(host_root: Path) -> Path:
    plan_path = host_root / "var" / "lib" / "uhome" / "ubuntu-apply-plan.sh"
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    plan_path.write_text(
        "\n".join(
            [
                "#!/usr/bin/env sh",
                "set -eu",
                'HOST_ROOT="/tmp/example"',
                "sudo mkdir -p /opt/uhome",
                "sudo systemctl daemon-reload",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return plan_path


def test_run_ubuntu_apply_plan_dry_run(tmp_path):
    host_root = tmp_path / "host"
    _write_plan(host_root)
    result = run_ubuntu_apply_plan(host_root, execute=False)
    assert result.ok is True
    assert result.commands[0]["executed"] is False
    assert result.report_path.exists()


def test_run_ubuntu_apply_plan_execute(tmp_path):
    host_root = tmp_path / "host"
    _write_plan(host_root)

    def _runner(command, shell, text, capture_output):
        del shell, text, capture_output
        return type("_Completed", (), {"returncode": 0, "stdout": f"ran {command}", "stderr": ""})()

    result = run_ubuntu_apply_plan(host_root, execute=True, runner=_runner)
    assert result.ok is True
    assert result.commands[0]["executed"] is True
    assert result.commands[0]["stdout"].startswith("ran ")
