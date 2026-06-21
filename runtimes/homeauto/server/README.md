# uHOME server runtime (`server/` in uHomeNest v3.9)

This subtree is the **uHOME** LAN server implementation inside **[uHomeNest](../README.md)** (**v3.9.x**). The former standalone GitHub repo was **`uHOME-server`**.

## Purpose

**uHOME** is a **home media and living-room computer**: a **media player**,
**controller-first** console/kiosk **TUI and thin-GUI**, and **decentralised
LAN server** for the household. It targets a **dual-role machine**—typically
**Linux** for uHOME plus an optional **Windows + Steam** side—installed and
refreshed through **`sonic-screwdriver`** (Ventoy/USB, recovery, and bootstrap),
**not** through Empire- or Wizard-centric flows.

The same stack offers a **curated on-disk library** of games and apps (vault /
library surfaces), **Jellyfin** playback, and **home automation** via **Home
Assistant**, surfaced through the **kiosk-style thin UX** (with `uHOME-matter`
owning bridge contracts and adapter assets).

## Ownership

- LAN-first household server (decentralised on your network, not a cloud hub)
- media playback, library, and presentation scheduling
- controller-first kiosk / thin console surfaces (TV, tablet, living room)
- Steam/Linux game-host and launcher integration on the Linux side
- automation job fulfilment **inside** uHOME’s thin automation lane
- curated library, vault reader, and Beacon-style offline content surfaces
- integration **hooks** for Home Assistant and Matter (contracts in `uHOME-matter`)

## Non-Goals

- generic USB/installer **product** (that stays with `sonic-screwdriver`)
- canonical family-wide runtime semantics (shared contracts may still align with `uDOS-core` where useful)
- macOS/iCloud-first sync (owned by Apple platform apps elsewhere)
- replacing a full desktop browser OS (kiosk/thin surfaces are intentional)

## Spine

- `services/`
- `scheduling/`
- `modules/`
- `docs/` — stable reference (aligned with uDOS `docs/`)
- `wiki/` — short units and orientation (aligned with family `wiki/`)
- `learning/` — study order and Library links (repo-local counterpart to Pages “learning” hub)
- `tests/`
- `scripts/`
- `config/`

## Local Development

Build service modules as explicit, testable units and keep managed state outside the repo.
Use `QUICKSTART.md` for the first runnable path and use
`examples/basic-uhome-server-session.md` for the smallest standalone smoke.

## Family Relation

**uHOME** is its **own product**: a media + console + LAN + automation hub for
the home. It is **not** defined as a sub-part of uDOS; cross-repo contracts
(e.g. sync-record shapes) are **compatibility layers**, not ownership.

Partners and siblings:

- **`sonic-screwdriver`** — install, recovery, dual-boot, and hardware bootstrap
  **into** uHOME (this pass treats Sonic as in-scope; Empire/Wizard are not the
  install story).
- **`uHOME-matter`** — Home Assistant and Matter **contracts** and bridge assets;
  the **kiosk thin UX** on `uHOME-server` is where operators **see** automation
  alongside media and games.
- **`uHOME-client`** and **mobile app repos** — remote/control clients; they do
  not own the household server role.
- **Household network policy** for normal LANs ships **in this repo**
  (`src/uhome_server/contracts/`). Optional alignment with other family hosts
  (e.g. Ubuntu command-centre) is **future**, not the product definition.

## Transitional Runtime Note

The runnable server and installer-adjacent flow remain in `src/uhome_server/` and
legacy-support roots such as `apps/`, `courses/`, `defaults/`, `examples/`,
`library/`, `memory/`, and `vault/`—including **curated library** and kiosk
surfaces that predate the current doc framing.

For runtime vs Sonic vs `uHOME-matter` boundaries, see `docs/base-runtime-boundary.md`.

## Quick Start

```bash
bash scripts/run-uhome-server-checks.sh
~/.udos/venv/uhome-server/bin/python -m uvicorn uhome_server.app:app --host 127.0.0.1 --port 8000 --reload
```

For the direct local console/kiosk launch path, use:

```bash
bash scripts/first-run-launch.sh
```

That bootstraps the repo, starts `uHOME-server`, activates the default local
presentation lane, and opens the console surface at
`http://127.0.0.1:8000/api/runtime/thin/automation`.

On macOS, the Finder wrapper is:

```bash
open ./scripts/first-run-launch.command
```

In another terminal:

```bash
curl http://localhost:8000/api/health
curl http://localhost:8000/api/runtime/ready
```

For local runtime bring-up (server, Jellyfin, kiosk), see `QUICKSTART.md`,
`FIRST-TIME-INSTALL.md`, and the documentation tree under `docs/`.

For operator env vars and preflight host checks, use
`docs/ENVIRONMENT-CONFIGURATION.md` and `bash scripts/check-prereqs.sh`.

## Activation

The v2 repo activation path is documented in `docs/activation.md`.

Run the current repo validation entrypoint with:

```bash
bash scripts/run-uhome-server-checks.sh
```

Shared sync-record contract tooling is also available through:

```bash
uhome contracts sync-record
uhome contracts validate-sync-record --input path/to/envelope.json
```

Runtime ingest and retrieval surfaces are available at:

```bash
POST /api/runtime/sync-records/ingest
GET /api/runtime/sync-records/latest
GET /api/runtime/sync-records
```

Bundled household networking policy (regular LAN; **`lan`** is the default profile) is available at:

```bash
GET /api/runtime/contracts/uhome-network-policy
GET /api/runtime/contracts/uhome-network-policy/schema
POST /api/runtime/contracts/uhome-network-policy/validate
```

Contracts live under `src/uhome_server/contracts/`. A future version may align with **uDOS-ubuntu** command-centre networking.
