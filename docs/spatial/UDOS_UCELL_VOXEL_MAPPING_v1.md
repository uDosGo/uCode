---
title: "uCell ↔ Voxel Mapping v1 (Locked)"
status: draft
last_updated: 2026-06-08T20:11:32+10:00
category: specification
tags: [[--public]]
description: "**Status:** Locked for v1.4 (Alpha)"
---
# uCell ↔ Voxel Mapping v1

**Status:** Locked for v1.4 (Alpha)

## Overview

This spec defines the mapping between **uCell** (economic unit) and **voxel** (spatial unit). It reconciles the **macrocube** model with the **spatial algebra**.

## Definitions

### uCell
- **Unit:** 1 uCell = 1 voxel (24×24×24 pixels).
- **Economy:** Used for storage, rendering, and transactions.

### Voxel
- **Unit:** 1 voxel = 1 uCell.
- **Coordinates:** `(x, y, z)` in 3D space.

## Macrocube

- **Definition:** A 6×6×6 cube of voxels (144×144×144 pixels).
- **uCell Equivalent:** 216 uCells (6³).
- **Use Case:** Large-scale surfaces (e.g., `uGridComposer`).

## Mapping Rules

1. **1:1 Mapping:**
   - 1 uCell = 1 voxel.
   - 1 macrocube = 216 uCells.

2. **Storage:**
   - uCells are stored in **Tower of Knowledge** slots.
   - Voxels are rendered via **spatial algebra**.

3. **API Paths:**
   - `/cell/{x}/{y}/{z}` — Access a voxel.
   - `/ucell/{id}` — Access a uCell.

## Examples

### uCode Commands
```bash
# Buy a uCell
udo ucell buy 1

# Map a uCell to a voxel
udo ucell map 1 --voxel 1 2 3

# Render a macrocube
udo macrocube render 1 2 3
```

### Localhost Surface
- **URL:** `http://localhost:3000/ucell/1`
- **Voxel Render:** `/cell/1/2/3`

## Reconciliation

| Unit | Size (Pixels) | uCells | Use Case |
|------|---------------|--------|----------|
| Voxel | 24×24×24 | 1 | Base unit |
| Macrocube | 144×144×144 | 216 | Large surfaces |

## See Also
- [UDOS_SPATIAL_ALGEBRA_LOCKED_v1.2.md](UDOS_SPATIAL_ALGEBRA_LOCKED_v1.2.md) — Spatial algebra.
- [UDOS_TOWER_OF_KNOWLEDGE_LOCKED_v1.md](UDOS_TOWER_OF_KNOWLEDGE_LOCKED_v1.md) — Slot storage.
