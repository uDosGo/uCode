---
title: "uCode3 — Console, Tablet & Layback Computing Runtime"
status: draft
last_updated: 2026-04-30T02:43:33+10:00
category: documentation
tags: [homenest, ucode3, ucode4]
description: "**Status:** Planning — Reference implementation: `~/Code/HomeKit/` (uHomeNest)"
---
# uCode3 — Console, Tablet & Layback Computing Runtime

**Status:** Planning — Reference implementation: `~/Code/HomeKit/` (uHomeNest)
**Slot Capacity:** 512 (2× uCode2, 4× uCode1)
**Theme:** Space / Elite
**Rendering:** Console / Tablet / Touch (2.5D spatial)
**Input:** Keyboard + Game Controller (layback mode)

---

## Core Identity

uCode3 bridges uCode2's grid/layer system and uCode4's true 3D. It adds **console-scale rendering**, **tablet/touch surfaces**, and the **layback computing** input model — using a game controller as a primary navigation device.

The **uHomeNest** project (`~/Code/HomeKit/`) serves as the reference implementation for uCode3's console/media server convergence. Its USXD console layouts, controller-first UX, and Jellyfin media backbone are the practical expression of the uCode3 concept.

### Key Differentiators from uCode2

| Dimension | uCode2 | uCode3 |
|-----------|--------|--------|
| **Rendering** | Web / React / Tailwind | Console / Tablet native |
| **Grid** | 2D (x, y) | 2D + layers (z = layer index) |
| **Spatial** | Grid cells | Map layers + R-tree index |
| **Input** | Keyboard + Mouse | Keyboard + Game Controller |
| **Surface** | Desktop browser | TV / Console / Tablet |
| **Deployment** | GitHub Pages | App Store / Console store |

---

## uCode3 Slot Architecture

```
┌──────────┬──────────────────────┬──────────────────────────────────┐
│ Slots    │ Type                 │ Purpose                          │
├──────────┼──────────────────────┼──────────────────────────────────┤
│ 0–63     │ Commands             │ Core + extended (from uCode2)    │
│ 64–127   │ Commands (extended)  │ Console/tablet-native commands   │
│ 128–255  │ Snacks               │ Executable containers            │
│ 256–383  │ Visual (ANSI/Emoji)  │ 2.5D-optimised visual overlays  │
│ 384–511  │ Aliases              │ Pointers to 0–255                │
└──────────┴──────────────────────┴──────────────────────────────────┘
```

### New Commands (Slots 64–127)

| Slot | Machine | Human | Emoji | Description |
|------|---------|-------|-------|-------------|
| 64 | `udos:console` | Console | 🎮 | "Launch console mode" |
| 65 | `udos:layback` | Layback | 🛋️ | "Enter layback computing mode" |
| 66 | `udos:controller` | Controller | 🕹️ | "Configure game controller" |
| 67 | `udos:spatial-nav` | SpatialNav | 🧭 | "Navigate spatial map" |
| 68 | `udos:teleport` | Teleport | 🌐 | "Jump to grid coordinate" |
| 69 | `udos:voice` | Voice | 🎤 | "Voice command input" |
| 70 | `udos:gesture` | Gesture | ✋ | "Gesture control input" |
| 71–127 | (reserved) | – | – | "Future console commands" |

---

## Layback Computing — Input Concept

Layback computing means: **lean back, game controller in hand, navigate the uDos universe from the couch.**

### Controller Button Map

| Controller | uCode3 Action | Description |
|------------|--------------|-------------|
| **D-pad Up/Down** | Navigate grid rows | Move selection vertically |
| **D-pad Left/Right** | Navigate grid columns | Move selection horizontally |
| **A button** | Activate | Open cell, launch snack, confirm |
| **B button** | Back | Return to previous screen, cancel |
| **X button** | Context menu | Show actions for selected item |
| **Y button** | Quick launch | Launch favourite/pinned snack |
| **Left stick** | Pan spatial view | Move around the map |
| **Right stick** | Scroll / rotate | Scroll text, rotate grid view |
| **L1** | Layer up | Move to next grid layer |
| **R1** | Layer down | Move to previous grid layer |
| **L2** | Zoom out | Zoom out of spatial view |
| **R2** | Zoom in | Zoom into spatial view |
| **Start** | Menu | Open system menu |
| **Select** | Map | Toggle minimap overlay |

### Touch Layout (Tablet)

| Gesture | Action |
|---------|--------|
| Tap | Select / activate |
| Long press | Context menu |
| Swipe left/right | Navigate between screens |
| Swipe up/down | Scroll content |
| Pinch | Zoom in/out on spatial view |
| Two-finger rotate | Rotate grid view |
| Three-finger swipe | Switch layer |

---

## Console/Tablet Rendering Pipeline

```
uCode2 grid (2D ASCII)
    │
    ├── GridLayer mapping (z-index stacking)
    │
    ├── uCode3 spatial layer (R-tree + 2.5D perspective)
    │       │
    │       ├── Console: terminal framebuffer (scaled)
    │       ├── Tablet: touch-optimised React Native / Tauri
    │       └── TV: 1080p/4K scaled from grid (chromecast/HDMI)
    │
    └── uCode4 (3D voxel — future)
```

### Spatial Layer Progression

| Layer Dimension | uCode1 | uCode2 | uCode3 | uCode4 |
|----------------|--------|--------|--------|--------|
| Axes | x, y | x, y | x, y, layer | x, y, z, t |
| Index | None | Linear | R-tree spatial | 3D octree |
| Snapping | Grid cells | Grid cells | Free-form coords | Volumetric regions |
| Rendering | ASCII | Web/React | Console/Tablet | 3D/VR |

---

## Game Controller as uCode3 Hardware

The game controller becomes the **primary input device** for uCode3.

### Hardware Profiles

| Controller | Platform | Notes |
|------------|----------|-------|
| Xbox / PlayStation | Console | Native support, rumble for feedback |
| Nintendo Switch Pro | Console | Gyro for gesture input |
| Steam Deck | Handheld | Built-in, full Linux stack |
| 8BitDo | Retro | Feels like NES/SNES — fits theme |
| Touch overlay | Tablet | Virtual gamepad on screen |

### Visual Feedback via Controller

- **Rumble** on cell activation, error, or notification
- **LED ring** colour reflects system status (green=ok, red=error, blue=idle)
- **Trigger resistance** for scroll boundary detection

---

## Theme: Space / Elite (Lexicon)

| Lane | Term | Meaning |
|------|------|---------|
| Dev | Galactic Encyclopedia | Universal knowledge repository |
| Story | Copilot | AI navigation assistant |
| Student | Star Charts | Advanced spatial-temporal mapping |
| Dev | Warp Drive | Instant knowledge retrieval |
| Story | Hyperspace | Real-time collaboration across space |

---

## Directory Structure

```
uCode3/                          ← Already exists as skeleton
├── core/                        ← Rust core (migrated from uCode2)
├── console/                     ← Console rendering engine (NEW)
│   ├── framebuffer/             ← Terminal framebuffer scaling
│   ├── gamepad/                 ← Game controller input layer
│   └── touch/                   ← Touch input abstraction
├── docs/
│   └── LAYBACK_COMPUTING.md     ← This document
└── spatial/                     ← Spatial ops (already built)
```

> **Note:** uCode3 is not a separate codebase — it's a configuration and rendering mode within uCode2. The spatial crate (`uCode2/spatial/`), TUI (`uCode2/tui/`), and grid system already provide the foundation. uCode3 activates when running in console mode with a game controller connected.
