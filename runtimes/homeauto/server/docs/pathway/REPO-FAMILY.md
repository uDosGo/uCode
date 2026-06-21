# Repo Family Model

Status: active

This document defines how **uHomeNest** (monorepo, **v3.9.x**) sits **next to** other repos: **uHOME
is its own product** (media, kiosk, LAN server, dual-boot-friendly, HA in thin
UX). Shared uDOS repos are **compatibility and education** neighbours, not the
definition of uHOME.

## Shared Questions

Every repo should still answer:

1. What product or pathway does this repo provide?
2. What surfaces does it read or write?
3. What services does it expose?
4. What modules are optional?
5. What **optional** shared contracts does it consume (if any)?

## Family Roles (uHOME-centric)

### uHomeNest — server runtime (was standalone `uHOME-server`)

Owns:

- **media** playback and library presentation (e.g. Jellyfin integration)
- **controller-first** kiosk / thin console and scheduling on the Linux host
- **decentralised LAN** household services
- **Steam/Linux** gaming and launcher surfaces; **curated** games/apps library
- thin UX that **surfaces Home Assistant** when `uHOME-matter` contracts are present

### `uHOME-matter`

Owns:

- Home Assistant and Matter **contracts**, bridge definitions, clone/target maps
- assets the **kiosk** consumes for automation visibility

### `sonic-screwdriver`

Owns:

- **Install, recovery, Ventoy/USB, dual-boot** bootstrap **into** uHOME
- generic hardware-facing workflows (uHOME must not swallow this product)

### `uDOS-core` (optional alignment)

May publish **shared** JSON contracts (e.g. sync-record shapes) that uHOME can
read when a sibling checkout exists—**compatibility**, not ownership of the uHOME
product.

### Client repos (`uHOME-client`, apps)

Own:

- remotes and companions; not the household server runtime

## Boundary Rules

- **uHomeNest** is **not** `sonic-screwdriver` and does not own the USB installer product.
- `sonic-screwdriver` does not redefine uHOME’s media/kiosk/automation architecture.
- Automation **contract** ownership stays in `uHOME-matter` even when transitional bridge code still lives in the server repo.
- uHOME is **not** a subordinate “service of uDOS”; cross-repo docs and contracts are **adjacent**, not hierarchical.

## Integration (optional)

Where the wider family still shares artifacts, uHOME may consume:

- **Sonic** install examples and paths for home deployments
- optional third-party contract JSON via explicit paths or env overrides (no default
  checkout of other family repos)

No requirement that Empire, Wizard, or Ubuntu command-centre flows define uHOME’s operator story.
