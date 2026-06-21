---
title: "Roadmap (v1 line)"
status: draft
last_updated: 2026-04-22T23:26:13+10:00
category: roadmap
tags: [roadmap, ucode3]
description: "Deliver a Linux-first decentralized home stream server with Jellyfin backbone, `~/media/` vault semantics, and USXD c..."
---
# Roadmap (v1 line)

## Goal

Deliver a Linux-first decentralized home stream server with Jellyfin backbone, `~/media/` vault semantics, and USXD controller-first browser UX.

## Milestones

1. Foundation and archive stabilization
2. Media vault scanning and search indexing
3. Playback orchestration and UI control loop
4. Ubuntu deployment hardening and release readiness
5. Sonic Home Express lite packager/installer lane (`sonic-home-express`)
6. uDOS-family compatibility and ecosystem spine integration
7. udev framework policies and device management

## Future lane: Sonic Home Express

`sonic-home-express` is planned as an optional lite Sonic-family on-ramp for uHomeNest:

- Build and sign portable `.she` bundles
- Install from file, USB, or channel URL
- Serve local LAN update channels (`stable`, `beta`, `edge`)
- Keep full Sonic-family integration as an upgrade path, not a hard dependency

Tracked brief: `docs/UDN-SONIC-001.md`.

## Execution

Detailed round planning lives in `dev/ROADMAP-ROUNDS.md`.
