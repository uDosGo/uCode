# uHOME Home Profile Decision

Status: active home profile lane  
Updated: 2026-03-03

## Purpose

uHOME defines the **home media, console, and LAN hub**—a **standalone product**,
not a sub-lane of uDOS:

- media playback and LAN-served libraries (e.g. Jellyfin)
- controller-first **kiosk / thin UX** (living-room and tablet)
- **decentralised** household server on the normal home network
- **Dual-boot** friendly (Linux uHOME + optional Windows/Steam) with
  **`sonic-screwdriver`** as the install/recovery path
- **Curated** on-disk library of games and apps
- **Home Assistant** integrated **through the thin UX**, with contracts in
  `uHOME-matter`

This is an active decision doc for the home profile direction, not a full
implementation manual. Historical implementation detail remains in
`docs/specs/UHOME-v1.5.md`.

## v2 Alignment Note

uHOME v2 master architecture direction is now integrated into active repo docs.
Canonical v2 runtime entrypoint:

- `docs/architecture.md`

That v2 architecture surface now captures:

- always-on local household runtime ownership
- controller-first kiosk and launcher model
- Jellyfin media lane and Steam-side game surfaces
- bundled LAN network policy profiles (including default **`lan`**)
- automation extension owned by `uHOME-matter`

This decision file remains useful for historical lane context, while v2 runtime
shape should be read from `docs/architecture.md` first.

## Decision

uHOME remains:

- local-first
- LAN-oriented and decentralised on the home network
- Sonic-bootstrap friendly (USB/Ventoy/dual-boot via `sonic-screwdriver`)
- controller-first kiosk and media/console experience
- Home Assistant aware **via thin UX** and `uHOME-matter` contracts
- separate from cloud-dependent media stacks

For v1.5, the canonical `uHOME` product shape is:

- `uHOME Server` as the primary certified home-profile deployment role
- `uHOME TV Node` as a bounded companion playback/appliance role

The `uHOME` user-facing runtime may be presented through:

- an Alpine thin-GUI kiosk surface
- a Steam-console-style living-room launcher surface

These are presentation modes for the same home-profile lane rather than
separate architecture stacks.

The home profile should favor readable configuration, deterministic local processing, and open-box media workflow definitions where practical.

## Core Architecture

### Source and playback model

- broadcast or local media sources feed a home node
- the home node records, processes, and stores media locally
- playback is served across the LAN to household devices

### Processing model

uHOME supports:

- scheduled recording
- rule-based capture
- post-processing jobs
- library organization
- metadata enrichment where allowed by policy

### Runtime ownership

- **uHomeNest** (this monorepo) owns the household Linux runtime: media, kiosk/thin UX,
  LAN services, local scheduling, and thin automation fulfilment on the box.
- **`uHOME-matter`** owns Home Assistant / Matter **contracts** fed into that UX.
- **`sonic-screwdriver`** owns **install, recovery, Ventoy/USB, and dual-boot**
  bootstrap **into** uHOME—not Empire/Wizard as the install story.
- Shared **`uDOS-core`** artifacts (when used) are **compatibility** for envelope
  shapes, not product ownership of uHOME.

## v1.5 Release Direction

For v1.5, uHOME work is focused on:

- packaging and profile clarity
- DVR and post-processing lane definition
- Sonic-installed home profile behavior
- thin-GUI and Steam-console presentation alignment for living-room use
- **standalone** home deployment: uHOME + Sonic without assuming a monorepo or
  external command-centre

The older hybrid-console and broad appliance exploration docs are not the
canonical v1.5 source of truth unless a shipped surface is explicitly promoted
into the active spec.

This lane should not block the general v1.5 release beyond the specific home-profile commitments tracked in the roadmap.

## Non-Negotiables

- local media remains the primary operational model
- household playback must work over LAN without requiring cloud mediation
- install and packaging rules must remain explicit and profile-aware
- home-profile workflows stay **local-first** and **kiosk-visible**; optional
  cross-repo contracts do not redefine the product

## Related Documents

- `docs/specs/UHOME-v1.5.md`
- `docs/STATUS.md`
- `docs/decisions/HOME-ASSISTANT-BRIDGE.md`
- `docs/decisions/SONIC-DB-SPEC-GPU-PROFILES.md`
