# uHOME thin UI and product feature completion

**Purpose:** single checklist of **remaining or in-flight** capabilities. Use with
[`../../../docs/ROADMAP-V4.md`](../../../docs/ROADMAP-V4.md) for phasing. **Thin browser lane** is intentionally
**Markdown → HTML + Tailwind Typography (`prose`)** only — no uDOS Workspace /
binder-backed reading shell.

**Status:** living document — tick items when done; add rows as scope clarifies.

## Thin browser surfaces (`/api/runtime/thin/*`)

- [x] Server-rendered **prose** page (`GET /api/runtime/thin/read`)
- [x] **Browse** markdown under `docs/` (`GET /api/runtime/thin/browse?rel=…`)
- [x] **Automation** status HTML (`GET /api/runtime/thin/automation`)
- [x] Compiled **`/static/thin/prose.css`** (rebuild: `thin-prose-build/`)
- [ ] Operator doc: default **port** called out consistently (see `QUICKSTART.md`)
- [ ] Optional: index page listing safe `docs/` paths (still no binder shell)
- [ ] Optional: auth or LAN-only guard for thin routes in production profiles

## Media and DVR (Phase 2 roadmap)

- [ ] Durable DVR rule model and schedule backend
- [ ] Job queue for recording, post-processing, handoff
- [ ] Jellyfin integration hardening beyond current scaffold
- [ ] Library path model for local disks and mounted partitions

## LAN topology and storage (Phase 3+)

- [ ] Failover / election model where multiple nodes matter
- [ ] Rich distributed library indexing / replication (beyond file-backed registry)

## Clients and living room (Phase 5)

- [ ] Stable contract for Android / TV / Apple TV apps
- [ ] Launcher and session semantics consumed by all remotes
- [ ] Playback handoff and target selection documented and tested end-to-end

## Operational product

- [ ] Optional: PyPI or container publish automation (manual path exists)
- [ ] Optional: Terraform / cloud templates

## Explicit non-goals (near term)

- uDOS **#binder** or **Workspace compile** as **operator-facing** uHOME features
- Replacing thin prose with a full SPA or binder document tree inside **uHomeNest** (off roadmap unless explicitly scoped)
