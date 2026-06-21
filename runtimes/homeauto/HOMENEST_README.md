# HomeNest

> **Living-room console for the uDos ecosystem**
> 
> HomeNest is a controller-first, 10-foot viewing console for media playback, home automation, TV/DVR, and system management — all powered by uCode3.

## Overview

HomeNest provides a unified living-room experience:

- **Media Browser** — Browse and play movies, TV shows, music
- **TV Guide** — EPG schedule grid with DVR scheduling
- **Automation Panel** — Launch OBF automation sheets
- **Feed Viewer** — Unified timeline for RSS, HA events, media scans
- **Music Player** — Album art with visualizer
- **Settings** — System configuration and first-run wizard

## Architecture

```
HomeNest Console (Vue 3 + Tailwind)
    ↓ MCP (Unix socket)
homenest-mcp (Rust)
    ↓
├── homenest-media   — Media scanner, mpv playback
├── homenest-tv      — EPG, DVR, live TV
├── homenest-spec    — OBF automation compiler
├── homenest-feed    — Feed/Spool viewer
├── homenest-grid    — Grid cell mapping
├── homenest-voice   — Voice assistant (HomeKit)
└── homenest-settings — System configuration
```

## Repositories

| Component | Location | Language |
|-----------|----------|----------|
| Console UI | `~/Code/uDosGo/ui/src/views/surfaces/homenest/` | Vue 3 |
| MCP Server | `~/Code/uDosGo/uCode3/homenest-mcp/` | Rust |
| Media | `~/Code/uDosGo/uCode3/homenest-media/` | Rust |
| TV/DVR | `~/Code/uDosGo/uCode3/homenest-tv/` | Rust |
| SpecLang | `~/Code/uDosGo/uCode3/homenest-spec/` | Rust |
| Feed | `~/Code/uDosGo/uCode3/homenest-feed/` | Rust |
| Grid | `~/Code/uDosGo/uCode3/homenest-grid/` | Rust |
| Voice | `~/Code/uDosGo/uCode3/homenest-voice/` | Rust |
| Settings | `~/Code/uDosGo/ui/src/views/surfaces/homenest/settings/` | Vue 3 |
| CLI Skill | `~/Code/uDosGo/udo/skills/homenest/` | Bash |

## Development

See [HOMENEST_ROADMAP.md](../../docs/HOMENEST_ROADMAP.md) for the full implementation plan.

## Status

| Phase | Status |
|-------|--------|
| Phase 0: Foundation Cleanup | 🟡 In Progress |
| Phase 1: Core Infrastructure | 🔴 Not Started |
| Phase 2: Media & TV | 🔴 Not Started |
| Phase 3: Feed & Automation | 🔴 Not Started |
| Phase 4: Voice & Settings | 🔴 Not Started |
| Phase 5: Polish & Deploy | 🔴 Not Started |
