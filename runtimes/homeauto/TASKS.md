# TASKS - v1 execution board

## Backlog

- [ ] [UHN-R3-004] Implement `/api/playback/start` target selection #feature
- [ ] [UHN-R4-003] Add service install units for Ubuntu 22.04/24.04 #infra
- [ ] [UHN-R5-001] Scaffold `sonic-home-express/` module and command tree #feature
- [ ] [UHN-R5-002] Define `.she` bundle and manifest contracts in docs + schema stubs #core
- [ ] [UHN-R6-001] Add install/verify dry-run command skeleton for Sonic Home Express #infra
- [ ] [UHN-R6-002] Add channel serve manifest and local distribution skeleton #infra
- [ ] [UHN-R7-001] Add Sonic compatibility adapter contract for future full-stack upgrade #core

## In Progress

- [ ] [UHN-R3-004] Implement `/api/playback/start` target selection #feature

## Blocked

- [ ] [UHN-R3-002] Controller runtime bindings for dpad/A/B/X/Y in browser
  - Blocked on initial `usxd-runtime.js` implementation details.

## Done

- [x] [UHN-R0-001] Archive pre-v1 codebase into `v0/` and push `v0-beta` tag
- [x] [UHN-R0-002] Scaffold v1 top-level server/ui/media-vault/scripts/docs/tests
- [x] [UHN-R1-001] Stabilize fresh v1 repository structure and docs #meta
- [x] [UHN-R1-002] Add deterministic media-vault fixture coverage #core
- [x] [UHN-R1-003] Wire API placeholder handlers to modular router flow #core
- [x] [UHN-R1-004] Add route registry + API contract tests for modular router #core
- [x] [UHN-R1-005] Add real Jellyfin start/stop wiring in `server/jellyfin/orchestrate.sh` #infra
- [x] [UHN-R2-004] Add media index persistence and incremental update logic #feature
