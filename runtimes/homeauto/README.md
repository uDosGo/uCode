# uCode3 — HomeNest (Application Layer)

**Ownership:** uDosGo  
**Core Language:** Python + Rust  
**CLI Command:** `uhome-server`  
**Status:** 🟢 Active  
**Size:** ~6.3M / 11K lines

---

## Overview

uCode3 is the **application layer** of the uDos ecosystem — a home media server, home automation bridge, and kiosk/console UI. It provides the uHomeNest product line: household media, kiosk/thin UI, LAN server, and Matter/Home Assistant bridges.

uCode3 may import from uCode2 (MCP client, vault reads, feed queries) but never from uCode4.

### What uCode3 Owns

- **Home Media Server** — Jellyfin integration, media scanning, playback
- **Home Assistant Bridge** — Matter contracts, device management, automation
- **Kiosk/Console UI** — Thin client runtime, controller-first UX
- **Installer/Bundle System** — Sonic installer, bundle management, health checks
- **Rust Crates (homenest-*):**
  - `homenest-mcp` — MCP server for HomeNest (media, TV, automation, system)
  - `homenest-media` — Media scanner, metadata workflow, mpv controller, subtitles
  - `homenest-tv` — EPG parser, HDHomeRun tuner, DVR scheduler, storage manager
  - `homenest-feed` — Feed spool, RSS poller
  - `homenest-automation` — Scene manager, rule engine, OBF launcher
  - `homenest-voice` — HomeKit bridge, Wyoming STT client, command dispatcher
  - `homenest-docs` — Documentation generator
  - `homenest-flatpak` — Flatpak packaging
  - `homenest-debian` — Debian packaging
  - `homenest-grid` — Grid system
  - `homenest-spec` — USX bundle compiler

### What Belongs to Other Layers

| Feature | Layer | Why |
|---------|-------|-----|
| Grid/cell coordinate system | uCode1 | Foundation layer |
| MCP Gateway (Python) | uCode2 | Services layer — uCode3 consumes via client |
| Vault Bridge | uCode2 | Services layer |
| Feed Spool | uCode2 | Services layer |
| Spatial primitives | uCode2 | Services layer |
| Sprites & BOBs | uCode2 | Services layer |
| 3D worlds, portals | uCode4 | Spatial/3D layer |

### Dependency Rule

```
uCode1 ──► uCode2 ──► uCode3 ──► uCode4
```

uCode3 may import from uCode2 (MCP client, vault API). uCode3 has no dependencies on uCode4.

---

## Quick Start

```bash
# Install
bash scripts/install.sh

# Start server
bash scripts/start.sh

# Health check
curl http://localhost:7890/api/health
```

See: `QUICKSTART.md`, `FIRST-TIME-INSTALL.md`, `docs/`

---

## Architecture

```
uCode3 (Python + Rust)
├── src/uhome_server/     — Python server (FastAPI)
│   ├── routes/           — API endpoints
│   ├── services/         — Business logic
│   ├── installer/        — Bundle/install system
│   ├── sonic/            — Sonic installer integration
│   └── ...
├── tinshed/              — Rust crates (homenest-*)
│   ├── homenest-mcp/     — MCP server for HomeNest
│   ├── homenest-media/   — Media scanner & player
│   ├── homenest-tv/      — TV/DVR system
│   ├── homenest-feed/    — Feed spool
│   ├── homenest-automation/ — Scene & rules
│   ├── homenest-voice/   — Voice assistant
│   └── ...
├── ui/                   — Tailwind + USXD browser surface
├── apps/                 — Application configs
├── config/               — Configuration files
└── scripts/              — Install/start/stop/healthcheck
```

---

## Development

```bash
git clone git@github.com:uDosGo/uCode3.git
cd uCode3
# Python server
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
# Rust workspace (tinshed)
cd tinshed
cargo build
```

---

## License

MIT

---

*Part of the uDos ecosystem. See [uCode2](https://github.com/uDosGo/uCode2) for the services layer and [uCode4](https://github.com/uDosGo/uCode4) for spatial/3D.*
.*
