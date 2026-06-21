"""uHOME hardware preflight checker."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class UHOMEHostProfileDefinition:
    profile_id: str
    display_name: str
    boot_mode: str
    target_roles: tuple[str, ...]
    hardware: "UHOMEHardwareProfile"
    required_probe_flags: tuple[str, ...] = ()
    recommended_probe_fields: tuple[str, ...] = ()


@dataclass(frozen=True)
class UHOMEHardwareProfile:
    min_cpu_cores: int = 4
    min_ram_gb: float = 8.0
    min_storage_gb: float = 256.0
    min_media_storage_gb: float = 2000.0
    min_tuner_count: int = 1
    rec_cpu_cores: int = 6
    rec_ram_gb: float = 16.0
    rec_storage_gb: float = 512.0
    rec_media_storage_gb: float = 4000.0
    rec_tuner_count: int = 2
    require_hdmi: bool = True
    require_gigabit: bool = True
    min_usb_ports: int = 2


DEFAULT_PROFILE = UHOMEHardwareProfile()
STANDALONE_LINUX_PROFILE = UHOMEHostProfileDefinition(
    profile_id="standalone-linux",
    display_name="Standalone Linux Host",
    boot_mode="standalone",
    target_roles=("media-server", "dvr", "launcher"),
    hardware=DEFAULT_PROFILE,
    required_probe_flags=(),
    recommended_probe_fields=("game_storage_gb",),
)
DUAL_BOOT_STEAM_NODE_PROFILE = UHOMEHostProfileDefinition(
    profile_id="dual-boot-steam-node",
    display_name="Dual-Boot Steam Node",
    boot_mode="dual-boot",
    target_roles=("media-server", "steam-console", "windows-gaming"),
    hardware=UHOMEHardwareProfile(
        min_cpu_cores=6,
        min_ram_gb=16.0,
        min_storage_gb=512.0,
        min_media_storage_gb=2000.0,
        min_tuner_count=1,
        rec_cpu_cores=8,
        rec_ram_gb=32.0,
        rec_storage_gb=1024.0,
        rec_media_storage_gb=8000.0,
        rec_tuner_count=2,
        require_hdmi=True,
        require_gigabit=True,
        min_usb_ports=4,
    ),
    required_probe_flags=("supports_windows_dual_boot", "steam_console_ready"),
    recommended_probe_fields=("game_storage_gb",),
)
HOST_PROFILES: dict[str, UHOMEHostProfileDefinition] = {
    STANDALONE_LINUX_PROFILE.profile_id: STANDALONE_LINUX_PROFILE,
    DUAL_BOOT_STEAM_NODE_PROFILE.profile_id: DUAL_BOOT_STEAM_NODE_PROFILE,
}


@dataclass
class UHOMEPreflightResult:
    passed: bool
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    probe: dict[str, Any] = field(default_factory=dict)
    profile_id: str = "default"
    profile_label: str = "Default uHOME Host"
    capability_checks: dict[str, dict[str, Any]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "profile_id": self.profile_id,
            "profile_label": self.profile_label,
            "issues": self.issues,
            "warnings": self.warnings,
            "capability_checks": self.capability_checks,
            "probe": self.probe,
        }


def get_host_profile(profile_id: str | None) -> UHOMEHostProfileDefinition | None:
    if not profile_id:
        return None
    return HOST_PROFILES.get(profile_id)


def _add_capability_check(
    checks: dict[str, dict[str, Any]],
    name: str,
    passed: bool,
    detail: str,
    role: str,
) -> None:
    checks[name] = {"passed": passed, "detail": detail, "role": role}


def _evaluate_host_capabilities(
    probe: dict[str, Any],
    host_profile: UHOMEHostProfileDefinition | None,
    issues: list[str],
) -> dict[str, dict[str, Any]]:
    if host_profile is None:
        return {}

    checks: dict[str, dict[str, Any]] = {}
    roles = set(host_profile.target_roles)

    if "media-server" in roles:
        storage_ready = probe.get("storage_ready", True) is not False
        media_storage = float(probe.get("media_storage_gb") or 0)
        passed = storage_ready and media_storage >= host_profile.hardware.min_media_storage_gb
        detail = "Storage lane can support media-server workloads." if passed else "Storage lane does not meet media-server requirements."
        _add_capability_check(checks, "storage_ready", passed, detail, "media-server")
        if not passed:
            issues.append("Host profile: storage_ready requirements not met for media-server role.")
        media_volume_ids = probe.get("media_volume_ids")
        storage_identity_ok = bool(probe.get("os_disk_id")) and isinstance(media_volume_ids, list) and bool(media_volume_ids)
        detail = (
            "OS disk and media volume identities are present."
            if storage_identity_ok
            else "OS disk or media volume identity evidence is missing."
        )
        _add_capability_check(checks, "storage_identity_present", storage_identity_ok, detail, "media-server")
        if not storage_identity_ok:
            issues.append("Host profile: storage identity evidence is required for media-server role.")

    if "dvr" in roles:
        tuner_count = int(probe.get("tuner_count") or 0)
        dvr_ready = probe.get("dvr_ready", True) is not False
        passed = dvr_ready and tuner_count >= host_profile.hardware.min_tuner_count
        detail = "Host can support DVR ingest and recording workflows." if passed else "Host cannot satisfy DVR role requirements."
        _add_capability_check(checks, "dvr_ready", passed, detail, "dvr")
        if not passed:
            issues.append("Host profile: dvr_ready requirements not met for DVR role.")

    if "launcher" in roles:
        passed = bool(probe.get("has_hdmi", False))
        detail = "Display output available for local launcher flows." if passed else "Display output missing for launcher role."
        _add_capability_check(checks, "launcher_ready", passed, detail, "launcher")
        if not passed:
            issues.append("Host profile: launcher_ready requirements not met for launcher role.")

    if "steam-console" in roles:
        passed = bool(probe.get("has_hdmi", False)) and bool(probe.get("steam_console_ready"))
        detail = "Steam console lane is available." if passed else "Steam console lane requirements are not satisfied."
        _add_capability_check(checks, "steam_console_ready", passed, detail, "steam-console")
        if not passed:
            issues.append("Host profile: steam_console_ready requirements not met for steam-console role.")

    if "windows-gaming" in roles:
        passed = bool(probe.get("supports_windows_dual_boot"))
        detail = "Windows dual-boot handoff is supported." if passed else "Windows dual-boot capability is not available."
        _add_capability_check(checks, "windows_dual_boot_ready", passed, detail, "windows-gaming")
        if not passed:
            issues.append("Host profile: supports_windows_dual_boot requirements not met for windows-gaming role.")
        dual_boot_layout_ok = bool(probe.get("windows_disk_id")) and bool(probe.get("os_disk_id"))
        detail = (
            "Linux and Windows disk identities are present."
            if dual_boot_layout_ok
            else "Linux or Windows disk identity evidence is missing."
        )
        _add_capability_check(checks, "dual_boot_disk_layout_present", dual_boot_layout_ok, detail, "windows-gaming")
        if not dual_boot_layout_ok:
            issues.append("Host profile: disk identity evidence is required for windows-gaming role.")

    return checks


def preflight_check(
    probe: dict[str, Any],
    profile: UHOMEHardwareProfile = DEFAULT_PROFILE,
    host_profile: UHOMEHostProfileDefinition | None = None,
) -> UHOMEPreflightResult:
    issues: list[str] = []
    warnings: list[str] = []
    active_profile = host_profile.hardware if host_profile is not None else profile
    cpu = probe.get("cpu_cores")
    if cpu is not None:
        if cpu < active_profile.min_cpu_cores:
            issues.append(f"CPU: {cpu} cores < minimum {active_profile.min_cpu_cores}.")
        elif cpu < active_profile.rec_cpu_cores:
            warnings.append(f"CPU: {cpu} cores meets minimum but {active_profile.rec_cpu_cores}+ recommended.")
    ram = probe.get("ram_gb")
    if ram is not None:
        if ram < active_profile.min_ram_gb:
            issues.append(f"RAM: {ram:.1f} GB < minimum {active_profile.min_ram_gb:.0f} GB.")
        elif ram < active_profile.rec_ram_gb:
            warnings.append(f"RAM: {ram:.1f} GB meets minimum but {active_profile.rec_ram_gb:.0f} GB recommended.")
    storage = probe.get("storage_gb")
    if storage is not None and storage < active_profile.min_storage_gb:
        issues.append(f"OS storage: {storage:.0f} GB < minimum {active_profile.min_storage_gb:.0f} GB.")
    media = probe.get("media_storage_gb")
    if media is not None:
        if media < active_profile.min_media_storage_gb:
            issues.append(f"Media storage: {media:.0f} GB < minimum {active_profile.min_media_storage_gb:.0f} GB.")
        elif media < active_profile.rec_media_storage_gb:
            warnings.append(
                f"Media storage: {media:.0f} GB, {active_profile.rec_media_storage_gb:.0f} GB recommended."
            )
    gigabit = probe.get("has_gigabit")
    if gigabit is not None and active_profile.require_gigabit and not gigabit:
        issues.append("Network: Gigabit Ethernet required.")
    hdmi = probe.get("has_hdmi")
    if hdmi is not None and active_profile.require_hdmi and not hdmi:
        issues.append("Display: HDMI output required for uHOME console mode.")
    tuners = probe.get("tuner_count")
    if tuners is not None:
        if tuners < active_profile.min_tuner_count:
            issues.append(f"Tuner: {tuners} found, at least {active_profile.min_tuner_count} required.")
        elif tuners < active_profile.rec_tuner_count:
            warnings.append(f"Tuner: {tuners} found, {active_profile.rec_tuner_count}+ recommended.")
    usb = probe.get("has_usb_ports")
    if usb is not None and usb < active_profile.min_usb_ports:
        warnings.append(f"USB: {usb} port(s), {active_profile.min_usb_ports}+ recommended.")
    bluetooth = probe.get("has_bluetooth")
    if bluetooth is not None and not bluetooth:
        warnings.append("Bluetooth: not detected.")
    if host_profile is not None:
        for flag in host_profile.required_probe_flags:
            if not probe.get(flag):
                issues.append(f"Host profile: required capability '{flag}' not detected.")
        for field_name in host_profile.recommended_probe_fields:
            if field_name not in probe:
                warnings.append(f"Host profile: recommended probe field '{field_name}' not provided.")
        if host_profile.profile_id == "dual-boot-steam-node":
            game_storage = probe.get("game_storage_gb")
            if game_storage is not None and game_storage < 500:
                warnings.append("Game storage: 500 GB+ recommended for dual-boot Steam nodes.")
    capability_checks = _evaluate_host_capabilities(probe, host_profile, issues)
    return UHOMEPreflightResult(
        passed=not issues,
        issues=issues,
        warnings=warnings,
        probe=probe,
        profile_id=host_profile.profile_id if host_profile is not None else "default",
        profile_label=host_profile.display_name if host_profile is not None else "Default uHOME Host",
        capability_checks=capability_checks,
    )
