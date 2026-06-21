from __future__ import annotations

from pathlib import Path

from uhome_server.installer.prerequisites import evaluate_host_prerequisites


def test_host_prerequisites_pass_with_linux_baseline(tmp_path):
    workspace_path = tmp_path / "workspace"
    storage_path = tmp_path / "media"
    workspace_path.mkdir()
    storage_path.mkdir()

    report = evaluate_host_prerequisites(
        system_name="Linux",
        kernel_release="5.15.0-100-generic",
        python_version=(3, 11, 8),
        storage_paths=[storage_path],
        workspace_path=workspace_path,
        command_paths={
            "systemctl": "/usr/bin/systemctl",
            "journalctl": "/usr/bin/journalctl",
            "curl": "/usr/bin/curl",
            "jq": "/usr/bin/jq",
        },
        systemd_runtime_present=True,
    )

    assert report.passed is True
    assert report.checks["platform"].ok is True
    assert report.checks["kernel"].ok is True
    assert report.checks["systemd_runtime"].ok is True
    assert report.warnings == []


def test_host_prerequisites_fail_when_kernel_systemd_and_paths_missing(tmp_path):
    missing_workspace = tmp_path / "workspace"
    missing_storage = tmp_path / "media"

    report = evaluate_host_prerequisites(
        system_name="Darwin",
        kernel_release="4.19.0",
        python_version=(3, 8, 18),
        storage_paths=[missing_storage],
        workspace_path=missing_workspace,
        command_paths={
            "systemctl": None,
            "journalctl": None,
            "curl": None,
            "jq": None,
        },
        systemd_runtime_present=False,
    )

    assert report.passed is False
    assert report.checks["platform"].ok is False
    assert report.checks["kernel"].ok is False
    assert report.checks["python"].ok is False
    assert report.checks["systemctl"].ok is False
    assert report.checks["systemd_runtime"].ok is False
    assert report.checks["workspace_path"].ok is False
    assert report.checks[f"storage:{missing_storage}"].ok is False
    assert len(report.warnings) == 3
