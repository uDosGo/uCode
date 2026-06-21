---
title: "L100–899 Grid Layer Map — Full Specification"
status: draft
last_updated: 2026-04-30T02:43:33+10:00
category: specification
tags: [ucode4]
description: "The uDos grid spans 8 level bands (L100–L899), each containing 100 levels of spatial data. This is the unified coordi..."
---
# L100–899 Grid Layer Map — Full Specification

## Overview

The uDos grid spans 8 level bands (L100–L899), each containing 100 levels of spatial data. This is the unified coordinate space across the runtime progression.

## Coordinate Format

```
L<level>-<gridXY>-<cellXY>-<layer>
L100-BB45-1010-2
│     │     │     │
│     │     │     └── Layer (0–9): sub-layer within cell
│     │     └──────── Cell YX (00–99 each): 10k cells per grid
│     └────────────── Grid YX (AA–ZZ): 676 grids per level
└──────────────────── Level (100–899): 8 bands × 100 levels
```

### Grid Coverage per Level

- **Grids per level:** 676 (AA–ZZ, 26×26)
- **Cells per grid:** 10,000 (00–99 × 00–99)
- **Layers per cell:** 10 (0–9)
- **Total cells per level:** 6,760,000
- **Total system capacity:** ~5.4 billion cells

---

## Level Bands

### L100–199: Dungeon / Underground

The classic adventure layer. ASCII dungeon grids, ACS-style maps, cave systems.

| Level | Name | Description | uCode2 | uCode3 | uCode4 |
|-------|------|-------------|--------|--------|--------|
| **L100** | Tutorial Dungeon | First room, welcome grid | ✅ Grid | ✅ Spatial | ⬜ Cavern |
| **L101** | Wizard's Chamber | Main vault UI | ✅ Grid | ✅ Spatial | ⬜ Wizard hall |
| **L102** | Hall of Records | Document storage | ✅ Grid | ✅ Spatial | ⬜ Library |
| **L103** | Treasure Vault | Snack/relic storage | ✅ Grid | ✅ Spatial | ⬜ Treasury |
| L104–110 | Tutorial wing | Learning levels | ⬜ | ⬜ | ⬜ |
| L111–150 | Crypt & catacombs | Deeper difficulty | ⬜ | ⬜ | ⬜ |
| L151–180 | Lava caverns | High-risk data | ⬜ | ⬜ | ⬜ |
| L181–199 | Deep dungeons | Endgame content | ⬜ | ⬜ | ⬜ |

### L200–299: Upside Down / Mirror

Reflected, inverted, or alternate-state grids. The mirror dimension.

| Level | Name | Description | uCode2 | uCode3 | uCode4 |
|-------|------|-------------|--------|--------|--------|
| **L200** | Mirror Entrance | Reflection of L100 | ⬜ | ⬜ | ⬜ |
| L201–220 | Inverted architecture | Opposite mappings | ⬜ | ⬜ | ⬜ |
| L221–250 | Shadow data | Backup/cold storage | ⬜ | ⬜ | ⬜ |
| L251–280 | Mirror maze | Complex navigation | ⬜ | ⬜ | ⬜ |
| L281–299 | Void | Empty/reset state | ⬜ | ⬜ | ⬜ |

### L300–399: Earth / Surface

Surface-level grids: terrain, cities, infrastructure.

| Level | Name | Description | uCode2 | uCode3 | uCode4 |
|-------|------|-------------|--------|--------|--------|
| **L300** | World Map | Surface overview | ⬜ | ⬜ | ⬜ |
| L301–320 | Urban grids | City layouts | ⬜ | ⬜ | ⬜ |
| L321–340 | Rural & wild | Natural terrain | ⬜ | ⬜ | ⬜ |
| L341–360 | Infrastructure | Roads, power, data | ⬜ | ⬜ | ⬜ |
| L361–380 | Underground surface | Subway, basements | ⬜ | ⬜ | ⬜ |
| L381–399 | Coastal & water | Shorelines, ports | ⬜ | ⬜ | ⬜ |

### L400–499: Atmosphere / Sky

Weather, broadcast, signal layers. Teletext and Ceefax pages.

| Level | Name | Description | uCode2 | uCode3 | uCode4 |
|-------|------|-------------|--------|--------|--------|
| **L400** | Sky Grid | Atmosphere overview | ⬜ | ⬜ | ⬜ |
| L401–420 | Weather layers | Wind, pressure, temp | ⬜ | ⬜ | ⬜ |
| L421–450 | Broadcast | Teletext pages 100–899 live here | ⬜ | ⬜ | ⬜ |
| L451–470 | Signal & comms | Radio, WiFi, network | ⬜ | ⬜ | ⬜ |
| L471–490 | Cloud grid | Virtual instances | ⬜ | ⬜ | ⬜ |
| L491–499 | Upper atmosphere | Near-space | ⬜ | ⬜ | ⬜ |

### L500–599: Space / Orbit

Celestial grids, orbital mechanics, interstellar maps.

| Level | Name | Description | uCode2 | uCode3 | uCode4 |
|-------|------|-------------|--------|--------|--------|
| **L500** | Star Grid | Space overview | ⬜ | ⬜ | ⬜ |
| L501–520 | Orbital grid | Satellite positions | ⬜ | ⬜ | ⬜ |
| L521–540 | Solar system | Planetary positions | ⬜ | ⬜ | ⬜ |
| L541–560 | Deep space | Stellar cartography | ⬜ | ⬜ | ⬜ |
| L561–580 | Nebula & phenomena | Abstract space data | ⬜ | ⬜ | ⬜ |
| L581–599 | Event horizon | System boundaries | ⬜ | ⬜ | ⬜ |

### L600–699: Virtual / Digital

Digital spaces: database grids, network topology, memory maps.

| Level | Name | Description | uCode2 | uCode3 | uCode4 |
|-------|------|-------------|--------|--------|--------|
| **L600** | Digital Grid | Cyberspace overview | ⬜ | ⬜ | ⬜ |
| L601–620 | Database grids | Table structures | ⬜ | ⬜ | ⬜ |
| L621–640 | Network topology | Node maps | ⬜ | ⬜ | ⬜ |
| L641–660 | Memory maps | Storage allocation | ⬜ | ⬜ | ⬜ |
| L661–680 | Process space | Running processes | ⬜ | ⬜ | ⬜ |
| L681–699 | Virtual constructs | AI/ML data spaces | ⬜ | ⬜ | ⬜ |

### L700–799: Meta / Abstract

Semantic layers, concept maps, AI reasoning spaces.

| Level | Name | Description | uCode2 | uCode3 | uCode4 |
|-------|------|-------------|--------|--------|--------|
| **L700** | Meta Grid | Abstract overview | ⬜ | ⬜ | ⬜ |
| L701–720 | Semantic layers | Meaning maps | ⬜ | ⬜ | ⬜ |
| L721–740 | Concept graphs | Idea connections | ⬜ | ⬜ | ⬜ |
| L741–760 | AI reasoning | Neural activations | ⬜ | ⬜ | ⬜ |
| L761–780 | Logic spaces | Rule systems | ⬜ | ⬜ | ⬜ |
| L781–799 | Meta constructs | Self-referential data | ⬜ | ⬜ | ⬜ |

### L800–899: Quantum / Unknown

Reserved for quantum states, temporal data, unknown phenomena.

| Level | Name | Description | uCode2 | uCode3 | uCode4 |
|-------|------|-------------|--------|--------|--------|
| **L800** | Quantum Grid | Temporal overview | ⬜ | ⬜ | ⬜ |
| L801–820 | Probability spaces | Wave functions | ⬜ | ⬜ | ⬜ |
| L821–840 | Temporal layers | Time-series data | ⬜ | ⬜ | ⬜ |
| L841–860 | Entanglement | Linked states | ⬜ | ⬜ | ⬜ |
| L861–880 | Unknown signals | Unidentified data | ⬜ | ⬜ | ⬜ |
| L881–899 | The Edge | System boundary | ⬜ | ⬜ | ⬜ |

---

## Layer Assignment per Cell

Each cell in any level has 10 sub-layers (0–9):

| Layer | Use |
|-------|-----|
| 0 | Base/terrain |
| 1 | Overlay 1 (infrastructure) |
| 2 | Overlay 2 (entities) |
| 3 | Annotation / metadata |
| 4 | Signal / aura |
| 5–7 | Reserved for stacking |
| 8 | Debug / editor |
| 9 | Temporary / scratch |

---

## Level Addressing in Code

```python
# Coordinate helpers (core_py.usxd.grid_parser)
def parse_cell_id(cell_id: str) -> dict:
    """
    'L100-BB45-1010-2' → {
        'level': 100,
        'grid_x': 'B', 'grid_y': 'B',  # AA–ZZ
        'cell_y': 10, 'cell_x': 10,     # 00–99
        'layer': 2
    }
    """
    parts = cell_id.split('-')
    level = int(parts[0][1:])  # Strip 'L'
    grid_xy = parts[1]          # e.g. 'BB45' → grid B-B, cell 45
    cell_xy = parts[2]          # e.g. '1010' → cell 10,10
    layer = int(parts[3])       # 0–9
    return {
        'level': level,
        'grid_x': grid_xy[0],
        'grid_y': grid_xy[1],
        'cell_x': int(cell_xy[:2]),
        'cell_y': int(cell_xy[2:]),
        'layer': layer,
    }
```
