# uCode4 — Spatial/3D Layer

**Ownership:** uDosGo  
**Core Language:** Python + Three.js  
**CLI Command:** `ucode` (runtime/educational)  
**Status:** 🟢 Active  
**Size:** ~1.0M / 1K lines

---

## Overview

uCode4 is the **spatial/3D layer** of the uDos ecosystem — providing virtual worlds, spatial computing, and 3D environment management. It builds on the grid/cell system from uCode1 and the sprite/BOB rendering from uCode2 to create immersive 3D spaces.

uCode4 may import from uCode2 (spatial primitives, coordinate system) and uCode1 (grid cell addressing) but never from uCode3.

### What uCode4 Owns

- **3D World Engine** — Virtual environment rendering and management
- **Spatial Computing** — Coordinate-based world building (L400-L499 Dimensions)
- **Virtual World Management** — Create, edit, and navigate 3D spaces
- **Scene Composition** — Layer sprites, BOBs, and teletext into 3D scenes
- **World Persistence** — Save/load world states
- **Portal System** — Inter-map gateways (L700-L799)
- **Three.js Frontend** — WebGL 3D viewport

### What Belongs to Other Layers

| Feature | Layer | Why |
|---------|-------|-----|
| Grid/cell coordinate system | uCode1 | Foundation — uCode4 consumes it |
| Sprites & BOBs (visual rendering) | uCode2 | Services layer — uCode4 consumes it |
| MCP Gateway | uCode2 | Services layer |
| Vault Bridge | uCode2 | Services layer |
| Home media, automation | uCode3 | Application layer |

### Dependency Rule

```
uCode1 ──► uCode2 ──► uCode3 ──► uCode4
```

uCode4 may import from uCode2 (spatial, sprites) and uCode1 (grid types). uCode4 has no dependencies on uCode3.

---

## CLI: `ucode` (Runtime/Educational)

```
ucode <command> [arguments] [flags]
```

| Command | Purpose | Example |
|---------|---------|---------|
| `world` | 3D world operations | `ucode world create --name "MyWorld"` |
| `scene` | Scene composition | `ucode scene add --world MyWorld --sprite player` |
| `camera` | Camera control | `ucode camera set --position 0,0,10` |
| `render` | Render world/scene | `ucode render --world MyWorld --output scene.png` |
| `portal` | Inter-map gateways | `ucode portal create --from L400-AA10-0000-0 --to L500-BB20-0505-0` |

---

## Quick Start

### Install
```bash
pip install ucode4
```

### Create a 3D world
```bash
ucode world create --name "MyWorld" --type dimension
ucode scene add --world MyWorld --sprite player --position 0,0,0
ucode camera set --position 0,0,10
ucode render --world MyWorld --output scene.png
```

### Create a portal
```bash
ucode portal create --from L400-AA10-0000-0 --to L500-BB20-0505-0
```

---

## Architecture

```
uCode4 (Python)
├── world/           — 3D world creation and management
├── scene/           — Scene composition (sprites, BOBs, teletext)
├── camera/          — Viewport and camera control
├── renderer/        — 3D to 2D projection and output
├── portal/          — Inter-map gateways (L700-L799)
├── spatial/         — Spatial query and neighbour resolution
├── persistence/     — World state save/load
└── cli/             — Command-line interface

uCode4 (JavaScript/Three.js)
└── 3dworld/         — WebGL frontend (Vite + Three.js)
    ├── src/main.js  — WorldRenderer class
    └── index.html   — 3D viewport
```

### Layer Bands for 3D Worlds

| Band | Range | Name | Purpose |
|------|-------|------|---------|
| 400-499 | L400-L499 | Dimensions | AR/VR, game worlds |
| 700-799 | L700-L799 | Portals | Inter-map gateways |

---

## Development

### Setup
```bash
git clone git@github.com:uDosGo/uCode4.git
cd uCode4
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

### Testing
```bash
pytest tests/
```

---

## License

MIT

---

*Part of the uDos ecosystem. See [uCode1](https://github.com/uDosGo/uCode1) for the grid/cell foundation and [uCode2](https://github.com/uDosGo/uCode2) for the services layer.*
