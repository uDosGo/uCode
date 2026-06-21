from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_first_run_launcher_script_exists() -> None:
    script = REPO_ROOT / "scripts" / "first-run-launch.sh"
    contents = script.read_text(encoding="utf-8")

    assert script.exists()
    assert "api/runtime/thin/automation" in contents
    assert "api/launcher/start" in contents
    assert "run-uhome-server-checks.sh" in contents


def test_first_run_command_wrapper_points_to_shell_script() -> None:
    wrapper = REPO_ROOT / "scripts" / "first-run-launch.command"
    contents = wrapper.read_text(encoding="utf-8")

    assert wrapper.exists()
    assert "first-run-launch.sh" in contents
