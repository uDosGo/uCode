---
title: "uCode4 — Interdimensional Spatial & 3D Runtime"
status: draft
last_updated: 2026-04-30T02:43:33+10:00
category: readme
tags: [ucode4]
description: "**Status:** Planning / Pre-Alpha"
---
# uCode4 — Interdimensional Spatial & 3D Runtime

**Status:** Planning / Pre-Alpha
**Slot Capacity:** 1024 (4× uCode2, 8× uCode1)
**Theme:** Omniverse / Interdimensional
**Rendering:** 3D spatial → true 3D
**Input:** Touch, motion, voice, game controller

---

## Core Identity

uCode4 is the **immersive, spatial, 3D runtime** for uDos. It inherits all slot/command/snack capabilities from uCode3 and adds true 3D rendering, multi-dimensional spatial indexing, and layback computing input modes.

### Key Differentiators

| Dimension | uCode1–2 | uCode3 | uCode4 |
|-----------|----------|--------|--------|
| **Rendering** | ASCII / Teletext | Console / Tablet / Touch | 3D volumetric |
| **Grid** | 2D (x, y) | 2D + layers (x, y, z=layer) | 3D (x, y, z, t) |
| **Input** | Keyboard | Keyboard + Game Controller | Touch + Motion + Voice |
| **Spatial** | Grid cells | Map layers | Volumes / Voxels |
| **Publishing** | Local | GitHub Pages + TV/Console | Metaverse / AR/VR |

---

## L100–899 Grid Layer Map

The grid layer system spans 8 level bands, each with 100 levels (L100–L899). This is the unified coordinate space across uCode2 (grid layers), uCode3 (spatial maps), and uCode4 (3D volumes).

| Band | Levels | Theme | uCode2 | uCode3 | uCode4 |
|------|--------|-------|--------|--------|--------|
| **L100–199** | 100 | Dungeon / Underground | 2D grid layers | Spatial map (2.5D) | Cavern voxels |
| **L200–299** | 100 | Upside Down / Mirror | Mirror grid | Reflected spatial | Inverted 3D |
| **L300–399** | 100 | Earth / Surface | Terrain grid | Height-map layers | 3D terrain mesh |
| **L400–499** | 100 | Atmosphere / Sky | Sky grid | Wind/weather layers | Volumetric sky |
| **L500–599** | 100 | Space / Orbit | Star grid | Orbital spatial | 3D starfield |
| **L600–699** | 100 | Virtual / Digital | Data grid | Network topology | 3D data viz |
| **L700–799** | 100 | Meta / Abstract | Concept grid | Semantic layers | Abstract 3D |
| **L800–899** | 100 | Quantum / Unknown | Reserved | Reserved | Temporal 3D |
| **L900+** | — | Custom / User | User-defined | User-defined | User-defined 3D |

### Coordinate Format

```
L<level>-<gridXY>-<cellXY>-<layer>
L100-BB45-1010-2  →  Level 100, grid BB45, cell 1010, layer 2
```

---

## uCode4 Slot Architecture

```
┌───────────┬─────────────────────┬───────────────────────────────┐
│ Slots     │ Type                │ Purpose                       │
├───────────┼─────────────────────┼───────────────────────────────┤
│ 0–127     │ Commands            │ Core + extended (from uCode3) │
│ 128–255   │ Snacks              │ Executable containers         │
│ 256–383   │ Visual (ANSI/Emoji) │ 3D-optimised visual overlays  │
│ 384–511   │ Aliases             │ Pointers to 0–255             │
│ 512–639   │ Spatial objects     │ 3D models, voxels, volumes    │
│ 640–767   │ Animation channels  │ Motion sequences, timelines   │
│ 768–895   │ Sound / Audio       │ 3D spatial audio sources      │
│ 896–1023  │ Reserved            │ Future expansion              │
└───────────┴─────────────────────┴───────────────────────────────┘
```

---

## Layback Computing — Input Concept

uCode4 introduces **layback computing**: interaction via game controller as primary input device, designed for couch/TV use.

| Input Mode | Device | Use Case |
|------------|--------|----------|
| Navigation | D-pad / left stick | Browse grids, menus |
| Selection | A button / right trigger | Activate cell, launch snack |
| Context | B button / left trigger | Back, cancel, context menu |
| Scroll | Right stick | Pan 3D view, scroll text |
| Zoom | L2/R2 shoulder | Zoom in/out on spatial view |
| Voice | Headset mic | "Show L500-AA00-0000-0" |
| Gesture | Touchpad / motion | Rotate 3D model, swipe |

---

## Interdimensional Theme — Lexicon

| Lane | Term | Meaning |
|------|------|---------|
| Dev | Omniverse | Multidimensional knowledge space |
| Story | Oracle Trinity | Three AI assistants working together |
| Student | Portals | Connections between different knowledge realms |
| Dev | Time Stream | Temporal knowledge navigation |
| Story | Reality Weaver | Generative knowledge creation |
| Student | Dimensional Gateways | Cross-realm data portals |

---

## Directory Structure

```
uCode4/
├── docs/
│   ├── README.md            ← This file
│   ├── LAYER_MAP.md          ← Full L100–899 grid layer spec
│   ├── SLOT_MAP.md           ← 1024-slot architecture
│   ├── LAyBACK_COMPUTING.md  ← Game controller input spec
│   └── 3D_SPATIAL.md         ← 3D voxel/volume rendering plan
├── core/                     ← Rust core (future)
├── render/                   ← 3D rendering (future)
└── input/                    ← Game controller / touch (future)
```
