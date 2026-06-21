# uHOME Install Lanes

This document is the operator-facing Phase 4 reference for the two supported
example install lanes in **uHomeNest**.

## Lane 1: Standalone Linux Host

Use this lane when `uHOME` is the primary Linux host without a Windows gaming
layer on the same machine.

Inputs:

- `examples/installer/bundles/standalone/`
- `examples/installer/probes/standalone-linux.json`

Expected evidence:

- `host_profile.profile_id = standalone-linux`
- `os_disk_id` present
- one or more `media_volume_ids`
- rollback token or rollback record present

Example flow:

```bash
uhome-installer preflight \
  --probe ./examples/installer/probes/standalone-linux.json \
  --host-profile standalone-linux

uhome-installer stage \
  --bundle-dir ./examples/installer/bundles/standalone \
  --probe ./examples/installer/probes/standalone-linux.json \
  --stage-dir ./tmp/uhome-stage-standalone

uhome-installer execute-stage \
  --stage-dir ./tmp/uhome-stage-standalone \
  --target-root ./tmp/uhome-target-standalone

uhome-installer apply-target \
  --target-root ./tmp/uhome-target-standalone \
  --host-root ./tmp/uhome-host-standalone

uhome-installer verify-target \
  --host-root ./tmp/uhome-host-standalone
```

Operator checks:

- `install-receipt.json` includes `host_profile_id`, `storage_identity_evidence`,
  and `rollback_evidence`
- promoted verification reports host-profile and rollback evidence as present
- a second `apply-target` produces reinstall context with the same bundle and
  host profile

## Lane 2: Dual-Boot Steam Node

Use this lane when Linux `uHOME` shares the machine with an auxiliary Windows
gaming install.

Inputs:

- `examples/installer/bundles/dual-boot/`
- `examples/installer/probes/dual-boot-steam-node.json`

Expected evidence:

- `host_profile.profile_id = dual-boot-steam-node`
- `supports_windows_dual_boot = true`
- `steam_console_ready = true`
- both `os_disk_id` and `windows_disk_id` present
- one or more `media_volume_ids`

Example flow:

```bash
uhome-installer preflight \
  --probe ./examples/installer/probes/dual-boot-steam-node.json \
  --host-profile dual-boot-steam-node

uhome-installer stage \
  --bundle-dir ./examples/installer/bundles/dual-boot \
  --probe ./examples/installer/probes/dual-boot-steam-node.json \
  --stage-dir ./tmp/uhome-stage-dual-boot
```

Operator checks:

- the install plan carries `host_profile_id = dual-boot-steam-node`
- the plan includes `enable_steam_console_mode`
- staged receipts include dual-boot disk identity evidence

## Rollback And Reinstall Evidence

For both lanes, Phase 4 closeout expects:

- staged receipts to include rollback and storage identity evidence
- promoted receipts to include reinstall context
- rollback metadata to remain available under `rollback/` and
  `var/lib/uhome/rollback/`

These example lanes are the canonical Phase 4 references for the current
installer surface.
