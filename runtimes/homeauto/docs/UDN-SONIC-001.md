---
title: "Sonic-Home-Express - Lite Packager Module for uHomeNest"
status: draft
last_updated: 2026-04-22T23:26:13+10:00
category: documentation
tags: [cli, sonic, ucode3]
description: "- **Document ID:** `UDN-SONIC-001`"
---
# Sonic-Home-Express - Lite Packager Module for uHomeNest

- **Document ID:** `UDN-SONIC-001`
- **Status:** Active
- **Version:** 1.0.0
- **Date:** 2026-04-16

## Objective

Define `sonic-home-express` as a lightweight packager/installer/distribution helper for uHomeNest that works standalone now and can upgrade to full Sonic-family later.

Core outcomes:

- Package uHomeNest components into `.she` bundles
- Verify/sign manifests and payload checksums
- Install from file, USB, or network channel with dry-run support
- Serve LAN channels (`stable`, `beta`, `edge`) for updates

## Module placement (planned)

```text
uHomeNest/
  sonic-home-express/
    cmd/{pack,install,serve}
    pkg/{bundle,manifest,handler,transport}
    templates/
    scripts/
    docs/
```

## Planned command surface

- `sonic-home-express pack --source ... --output ... --version ... --channel ...`
- `sonic-home-express sign --bundle ... --key ...`
- `sonic-home-express verify <bundle>`
- `sonic-home-express install <bundle|--usb|--channel ...> [--dry-run] [--preseed ...]`
- `sonic-home-express serve --bundles ... --channels stable,beta,edge`

## Bundle contract (`.she`)

Planned sections:

- fixed header (`magic`, `version`, `size`)
- `manifest.json` (components, dependencies, checksums, channel/version metadata)
- signature block (Ed25519)
- payload blocks (`base`, `docker`, `venv`, `assets`, scripts)
- optional delta payloads

## Integration boundaries

- **v1 scope:** lite CLI, contracts, and local distribution only
- **non-goals:** full Ventoy flow, dual boot management, fleet orchestration, GUI installer
- **future:** compatibility adapter to full Sonic-family tools when present

## Delivery checkpoints

1. Spec and scaffolding
2. Pack/sign/verify baseline
3. Install flow and dry-run
4. Serve/channel metadata and USB helper flow
5. Compatibility adapter and hardening tests

## Related

- `docs/ROADMAP.md`
- `dev/ROADMAP-ROUNDS.md`
