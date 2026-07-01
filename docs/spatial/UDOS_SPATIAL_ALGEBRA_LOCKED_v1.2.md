---
title: "Spatial Algebra v1.2 (Locked)"
status: draft
last_updated: 2026-06-08T20:11:32+10:00
category: specification
tags: [[--public]]
description: "**Status:** Locked for v1.4 (Alpha)"
---
# Spatial Algebra v1.2

**Status:** Locked for v1.4 (Alpha)

## Overview

The **spatial algebra** defines the core geometry for uDos surfaces, cells, and cubes. It reconciles **voxel**, **2×3 cell**, and **depth cube** models into a unified coordinate system.

## Components

### 1. Voxel
- **Definition:** A single unit in 3D space.
- **Size:** 24×24 pixels (default).
- **Coordinates:** `(x, y, z)` where `z` is depth (0–5).

### 2. 2×3 Cell
- **Definition:** A 2×3 grid of voxels (48×72 pixels).
- **Layers:** L300–L700 (100-unit increments).
- **Use Case:** Teletext grid, USXD blocks.

### 3. Depth Cube
- **Definition:** A 6-layer stack of 2×3 cells.
- **Dimensions:** 48×72×144 pixels (6 layers × 24px depth).
- **API Paths:**
  - `/cell/{x}/{y}/{z}` — Single cell access.
  - `/cube/{x}/{y}` — Full cube access.

### 4. Binder
- **Definition:** A collection of cubes forming a surface.
- **Example:** A **uGridComposer** surface binds multiple cubes.

## Layers

| Layer | Purpose |
|-------|---------|
| L300  | Base (teletext) |
| L400  | Mid (USXD blocks) |
| L500  | High (sprites) |
| L600  | Overlay (emoji) |
| L700  | Top (UI chrome) |

## API Paths

- **Cell:** `/cell/{x}/{y}/{z}`
- **Cube:** `/cube/{x}/{y}`
- **Surface:** `/surface/{id}`

## Reconciliation

- **Macrocube:** A 6×6×6 cube of voxels (144×144×144 pixels).
- **Algebra Mapping:** Macrocube → 2×3 cell grid → depth cube.

## Examples

### uCode Commands
```bash
# Navigate to a cell
udo cell 1 2 0

# Render a cube
udo cube 1 2

# Bind cubes into a surface
udo surface create my-surface --cubes "1,2" "3,4"
```

### Localhost Surface
- **URL:** `http://localhost:3000/surface/my-surface`
- **USXD Blocks:** Rendered via `uGridComposer`.

## See Also
- [UDOS_UCELL_VOXEL_MAPPING_v1.md](UDOS_UCELL_VOXEL_MAPPING_v1.md) — Economy mapping.
- [UDOS_TOWER_OF_KNOWLEDGE_LOCKED_v1.md](UDOS_TOWER_OF_KNOWLEDGE_LOCKED_v1.md) — Slot storage.
