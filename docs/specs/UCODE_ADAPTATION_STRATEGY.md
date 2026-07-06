# uCode Classic Game Adaptation Strategy

**Status:** 🔒 LOCKED — Canonical Reference
**Version:** 1.0
**Date:** 2026-07-06

## Platform Architecture

```
┌─────────────────────────────────────────────────────┐
│                  uCode Platform                       │
├─────────────────────────────────────────────────────┤
│  Core Runtime: BBC BASIC for SDL 2.0                │
│  Add-on:       AMOS Runtime (sprites, BOBs, AMAL)   │
│  Foundation:   LENS, SKIN, MCP, Spool, Feed         │
│  Display:      GridCore UI (Teletext + Terminal)     │
│  Container:    Program (.ucode bundle)               │
└─────────────────────────────────────────────────────┘
```

## Adaptation Strategies by Game Type

### 1. Native BBC BASIC (Zero Effort)

| Game | Platform | Strategy |
|------|----------|----------|
| BBC Micro teletext games | BBC Micro | Run unchanged in uCode BBC BASIC runtime |
| Modern BBC BASIC programs | uCode | Already native |

**Key:** Every uCode1 (teletext-only) program runs unchanged on uCode2 (with sprites/BOBs). The teletext layer is always the base.

### 2. Assembly Preservation (Low-Medium Effort)

| Original Game | Platform | Adaptation Method | LENS Extraction |
|---------------|----------|-------------------|-----------------|
| **Elite** | BBC Micro (6502 ASM) | Re-assemble with BeebAsm → BBC BASIC runtime | Ship status, location, inventory |
| **Apple Panic** | Apple II (6502 ASM) | Cycle-accurate 6502 emulation (Rust component) | Screen state, score |
| **Repton** | BBC Micro (6502 ASM + Reptol) | Emulation + asset extraction | Reptol scripts, maps, sprites |

### 3. Text Adventure Migration (Low Effort)

| Original Game | Platform | Adaptation Method |
|---------------|----------|-------------------|
| **Adventure Construction Set** | Apple II | 6502 emulation → LENS extracts maps/rooms/items → SKIN exports |
| **Eamon** | Apple II | BBC BASIC interpreter + disk images → Teletext display |
| **NetHack** | Various (ASCII) | BBC BASIC port → teletext display |

### 4. AMOS-Style Sprite/BOB System

| AMOS Concept | uCode Implementation | Storage |
|--------------|---------------------|---------|
| **Sprite** (8 max, 16px wide) | GridCore UI Character (grid-aligned) | Character Set (YAML + glyph assets) |
| **BOB** (unlimited, any size) | GridCore UI Object (GIF animation) | `.gif` repository with metadata |
| **AMAL script** (independent movement) | MCP command sequence | JSON command definitions |
| **Sprite Bank** | Character Collection | YAML manifest + sprite sheets |

### 5. AMAL → MCP Bridge

| AMAL Script | uCode MCP Equivalent |
|-------------|----------------------|
| `MOVE(100,200,10,SIN)` | `MCP > sprite:1 command:animate path=wave x=100 y=200 speed=10` |
| `AUTO=1` | `MCP > sprite:1 command:set_property auto_animate=1` |
| `BOUNCE=1` | `MCP > sprite:1 command:set_property bounce=1` |

### 6. GIF-Based BOB Animations

| BOB Feature | uCode Implementation |
|-------------|----------------------|
| Multi-frame animation | GIF decoder (Rust) with frame timing |
| Transparency | Pixel-perfect collision masks from alpha channel |
| Palette remapping | SKIN applies new colour palettes to GIF frames |
| Loop control | `LoopMode` (Infinite, Once, Count) |

### 7. Modern BBC BASIC (Line Numbers Optional)

| Classic BBC BASIC | Modern uCode BBC BASIC |
|-------------------|------------------------|
| Line numbers required | **Optional** (use `PROC`/`FN` instead of `GOTO`/`GOSUB`) |
| Teletext Mode 7 | Full support via GridCore UI |
| VDU command stream | Routed to CEETEX teletext renderer |
| No sprite/BOB support | **Add-on:** AMOS Runtime enables sprites/BOBs |

### 8. Teletext Rendering (CEETEX Integration)

| CEETEX Feature | uCode Adaptation |
|----------------|------------------|
| Mode 7 teletext engine | VDU stream from BBC BASIC → GridCore UI teletext layer |
| 3-digit page navigation | MCP commands (`PAGE 101`, `NEXT`, `PREV`) |
| RSS feeds as pages | BBC BASIC programs generate teletext content |
| Textual terminal output | Spool export to ANSI, HTML, PNG via SKIN |

## Program Container Format

Programs replace the former "Snack/Snackpack" terminology for game/adventure bundles:

```yaml
# programs/adventure_demo/program.yaml
program:
  name: "Teletext Adventure"
  version: "1.0"
  type: "ucode"  # unified
  
  entry: "game.bbc"
  runtime: "bbc_basic_sdl"  # or "amos_addon"
  
  assets:
    teletext:
      - "text/title_page.ttx"
    sprites:      # optional (AMOS add-on)
      - "sprites/player_*.png"
    bobs:         # optional (AMOS add-on)
      - "bobs/explosion.gif"
    sounds:       # optional
      - "sounds/jump.wav"
  
  lens:
    capture:
      - screen    # 40x25 grid
      - variables # HP, gold, position
  
  skin:
    default: "teletext_classic"
    alternates: ["paper_retro", "dark_mode"]
  
  mcp:
    commands: ["PAGE", "NEXT", "PREV", "SAVE", "LOAD"]
```

## Game-Specific Adaptation Details

### Elite (BBC Micro)

```
Adaptation: Re-assemble 6502 source with BeebAsm → binary runs in BBC BASIC runtime
LENS extracts: ship_status, location, inventory
SKIN themes: elite_classic (green wireframe on black), paper_retro, dark_mode
MCP commands: PAUSE, SAVE, LOAD, JUMP, DOCK
Entry: elite.ssd (disc image)
```

### NetHack (ASCII)

```
Adaptation: Port to BBC BASIC, run in uCode runtime
LENS extracts: dungeon state, inventory, monster positions
Display: Teletext layer (ASCII → MODE 7)
```

### Apple Panic (Apple II 6502)

```
Adaptation: Cycle-accurate 6502 emulation (Rust component)
LENS extracts: screen state, score, level
MCP commands: SPEED, INJECT, PAUSE, RESUME
```

### Repton (BBC Micro)

```
Adaptation: Emulation + asset extraction
LENS extracts: Reptol scripts, maps (M files), sprites (S files)
SKIN: Generate new levels or export to modern formats
```

## Migration Path Summary

| Classic System | uCode Adaptation | Effort |
|----------------|------------------|--------|
| BBC Micro teletext game | Run unchanged in BBC BASIC | **Zero** |
| AMOS game (sprites/BOBs) | Port sprite/BOB calls to BBC BASIC + AMOS add-on | Low |
| Apple II ACS adventure | Emulate 6502, LENS extracts data | Medium |
| Amiga AMAL scripts | Convert to MCP commands | Medium |
| GIF animations | Load via AMOS add-on, render via GridCore UI | Low |

## Example: Teletext + Sprites Hybrid

```bbcbasic
   10 REM uCode Program: Teletext + Sprites
   20 
   30 MODE 7                     REM Teletext background
   40 PROC_init_graphics         REM AMOS add-on for sprites
   50 
   60 REM Load sprite (becomes GridCore UI Character)
   70 player = FN_load_sprite("player.png", 24, 24)
   80 PROC_sprite_place(player, 10, 12)
   90 
  100 REM Teletext overlay
  110 COLOUR 2                   REM Green text
  120 PRINT TAB(5,22) "Score: "; score
  130 
  140 REM MCP command (control from outside)
  150 cmd$ = FN_MCP_Poll()
  160 IF cmd$ = "SAVE" THEN PROC_save_game
  170 IF cmd$ = "QUIT" THEN END
```

## Immediate Implementation Priorities

1. BBC BASIC for SDL 2.0 as the core runtime
2. Port the AMOS Runtime add-on (sprites, BOBs, AMAL)
3. Build the GIF decoder (Rust) for BOB animations
4. Create example Programs (teletext-only and teletext+sprites)
5. Document MCP commands for sprite/BOB control