---
title: "uCode3 × HomeKit — Console/Media Server Convergence"
status: draft
last_updated: 2026-04-30T02:43:33+10:00
category: documentation
tags: [homekit, homenest, iot, ucode3, ucode4]
description: "**uHomeNest** (`~/Code/HomeKit/`) is the reference implementation for uCode3's console/tablet/touch + layback computi..."
---
# uCode3 × HomeKit — Console/Media Server Convergence

**uHomeNest** (`~/Code/HomeKit/`) is the reference implementation for uCode3's console/tablet/touch + layback computing runtime.

## Why HomeKit is uCode3

| uCode3 Feature | HomeKit Implementation |
|----------------|----------------------|
| **Console rendering** | USXD console layouts (`ui/usxd/launcher.json`) |
| **Controller input** | Blocked task `UHN-R3-002`: "Controller runtime bindings for dpad/A/B/X/Y in browser" |
| **Touch/tablet UI** | Tailwind CSS browser surface with USXD components |
| **Layback computing** | Jellyfin media player — couch-friendly, remote-control-first |
| **Spatial layers** | Media vault indexing + sonic-home-express bundle management |
| **TV/HDMI output** | Jellyfin stream server → TV via HDMI/Roku/Chromecast |
| **Sonic Home Express** | `.she` bundle format — snack-like executable containers for home automation |

## USXD Bridge

HomeKit already uses USXD as its layout format — the same format built in uCode2's pipeline:

```
HomeKit/ui/usxd/           uCode2/core_py/usxd/
├── launcher.json    ←──→  ASCII Grid Parser → USXD document
├── media-browser.json      Component Mapper → ThinUI renderer
├── now-playing.json        Grid Renderer → Terminal / Web
├── settings.json
├── components/
└── themes/
```

## Convergence Roadmap

| Step | What | Where |
|------|------|-------|
| 1 | Wire uCode2 USXD pipeline → HomeKit USXD consumer | `uCode2/core_py/usxd/` → `HomeKit/ui/usxd/` |
| 2 | Implement controller bindings (dpad/A/B/X/Y in browser) | `HomeKit/ui/usxd-runtime.js` |
| 3 | Port layback computing mode to HomeKit surfaces | `HomeKit/ui/` + `uCode2/tui/` |
| 4 | Add spatial layer maps (L100–899) to media vault | `HomeKit/media-vault/` |
| 5 | Sonic Home Express → snack-compatible bundles | `HomeKit/sonic-home-express/` |

## Key Contact Points

- `HomeKit/TASKS.md` — `[UHN-R3-002]` blocked on USXD runtime implementation
- `HomeKit/docs/USXD_GUIDE.md` — Full USXD format spec for HomeKit
- `HomeKit/server/` — FastAPI server with Jellyfin orchestration
- `HomeKit/ui/` — Tailwind + USXD browser surface
