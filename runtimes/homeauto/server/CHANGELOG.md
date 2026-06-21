# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `docs/thin-ui-feature-completion.md` — living checklist for thin UI lanes and product backlog.
- Thin **Tailwind Typography** bundle (`static/thin/prose.css`, built from `thin-prose-build/`)
  and HTML surfaces: `GET /api/runtime/thin/read` (default markdown intro), `GET /api/runtime/thin/browse`
  (markdown under `docs/` via `rel=` query), cross-links with `/api/runtime/thin/automation`.
- **`markdown`** dependency for server-side markdown rendering in thin read/browse mode.
- `uhome migrate wizard-to-kiosk`: copies `memory/wizard/uhome/presentation.json` to
  `memory/kiosk/uhome/`, rewrites `wizard_mode_active` → `kiosk_local_session` in that
  JSON, and updates `library/**/container.json` (`wizard_only` → `thin_kiosk_only`,
  `callable_from` `wizard` → `thin-kiosk`). Flags: `--dry-run`, `--force`,
  `--remove-legacy`, `--skip-presentation`, `--skip-manifests`.
- Bundled household network policy contract + schema in `src/uhome_server/contracts/`
  with a default **`lan`** profile for regular home/office LANs (no `uDOS-wizard` checkout)
- `GET /api/runtime/contracts/uhome-network-policy/schema`
- Health and readiness endpoints (`/api/health`, `/api/ready`, `/api/debug/registries`)
- Backup and restore CLI commands (`uhome backup create`, `uhome backup restore`, `uhome backup list`)
- Shared sync-record contract inspection and envelope validation commands (`uhome contracts ...`)
- Runtime sync-record ingest and retrieval endpoints backed by file-based envelope storage
- Sync-envelope ingest supports standard family sync-record envelopes
- Comprehensive operational runbooks (6 guides covering storage, nodes, registries, degradation)
- Deployment Guide for Ubuntu 20.04+ LTS systems
- Post-install validation script for automated deployment verification
- Docker Compose production template with health checks and resource limits
- Observability guide with monitoring, alerting, and capacity planning
- Operations README as central navigation hub for all operational documentation

### Changed
- **Planning:** uHOME **does not** ship uDOS **#binder / Workspace** as operator UX;
  thin surfaces stay **Markdown + Tailwind Prose** (`docs/contributor-dev-brief.md`,
  `docs/UHOME-DEV-ROADMAP.md`). **`sync_records`** `binder_*` fields remain for optional
  **`integrated-udos`** JSON only (`sync_records` module docstring).
- **`QUICKSTART.md`:** thin UI URLs and default **`8000`** port called out for browser proof.
- **Code decoupling:** sync-record contract + schema ship under `uhome_server/contracts/`
  (no `uDOS-core` path); optional overrides `UHOME_SYNC_RECORD_CONTRACT_PATH` /
  `UHOME_SYNC_RECORD_SCHEMA_PATH`. Removed `get_udos_family_root` from server config.
- Network policy validation module renamed to `uhome_network_policy.py` (replaces
  `wizard_policy.py`). Workflow/automation contract metadata points at
  `uhome_server/contracts/*.json` identifiers; default automation `origin_surface` is
  `uHOME-kiosk`. Launcher state is written under `memory/kiosk/uhome/` (still reads
  legacy `memory/wizard/uhome/` if present). JSON config accepts `legacy-uhome.json`
  before `wizard.json`.
- **uHOME-client:** bundled `src/runtime-services.json`; profiles are standalone with
  `shell_adapter` `thin-kiosk`; optional orchestration via   `UH_EXTERNAL_ORCHESTRATION_CONTRACT_PATH`
  and transport `orchestration-assisted` only. Family root: prefer `UHOME_FAMILY_ROOT`,
  with legacy fallback `UDOS_UHOME_FAMILY_ROOT`.
- Library catalog: `wrapper_route` field, `thin-kiosk` / `thin_kiosk_only` terminology
  (still accepts legacy `wizard` / `wizard_only` in manifests).
- Product docs (`README`, `docs/architecture.md`, `base-runtime-boundary.md`,
  `uHOME-spec.md`, pathway `REPO-FAMILY.md`) reposition **uHOME** as a standalone
  media + controller-first kiosk + decentralised LAN + dual-boot (Sonic) +
  curated library + HA-via-thin-UX product—not a sub-part of uDOS; **`uHOME-matter`**
  README aligned for kiosk-visible automation
- Network policy loads from the uHOME package bundle; `policy_owner` payloads use
  `uHOME-server`. `/api/runtime/contracts/uhome-network-policy` includes `routes`,
  `deployment`, and `future_integration` metadata (replaces `wizard_routes` on that payload).
- `/api/runtime/contracts/workflow-automation`: `workflow_owner` is `uHOME-server` for the
  standalone stream; `integration_note` mentions optional future **uDOS-ubuntu** coordination.
- Improved backup timestamp resolution to include microseconds (prevents filename conflicts)

### Deprecated
- None

### Removed
- Coupling to `uDOS-empire` for runtime info and related docs/templates

### Fixed
- None

### Security
- None

## [0.1.0] - 2026-03-10

Initial development release with Phase 5 and Phase 6 (partial) deliverables.

### Added
- FastAPI-based REST server with async request handling
- Household-safe media browsing API with keyword filtering
- Playback status and handoff API for living-room clients
- Launcher capability model and status API
- Node and storage registry system for multi-node deployments
- Library catalog with Jellyfin integration
- Home Assistant bridge service (optional)
- DVR scheduling system (foundation)
- Presentation launcher management (thin-gui, steam-console)
- Installer and preflight system for Ubuntu deployments
- CLI tools: `uhome launcher`, `uhome installer`, `uhome backup`
- 131 comprehensive unit and integration tests
- Development documentation and architecture guides

### Technical Foundation
- Python 3.9+ with type hints and dataclasses
- FastAPI with Pydantic validation
- File-based registries for decentralized node coordination
- Graceful degradation patterns for partial system failures
- Workspace-based configuration system
- Service singleton pattern for shared state

### Documentation
- 6 operational runbooks (storage, nodes, registries, cache, shutdown, degradation)
- Ubuntu 20.04+ deployment guide (11-phase walkthrough)
- Observability guide (monitoring, alerting, capacity planning)
- Release policy documentation (semantic versioning, workflow)
- Phase 1-6 architecture documents and checklists
- Development roadmap and migration status

### Quality Assurance
- 131 passing tests across all modules
- Test coverage for health endpoints, backup/restore, registries, routes, services
- Automated CI validation (tests, linting)
- Post-install validation script for deployment verification

## [0.0.1] - 2026-01-01

Initial project setup (placeholder).

### Added
- Repository structure
- Basic Python package configuration
- Initial CI/CD setup

---

**Note**: This changelog started being maintained consistently from v0.1.0 onwards. Earlier changes may be incomplete.
