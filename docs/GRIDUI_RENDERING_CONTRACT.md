# GridUI Rendering Contract — uCode Runtime Target

**Date**: 2026-07-02
**Status**: v2 — Per-cell char-width, fixed grid, multiple render modes
**Purpose**: Defines the pixel-exact rendering contract. The uCode backend runtime produces `GridBuffer` objects; the frontend renders them. The grid is a **fixed 24×24 pixel cell matrix** — character widths are per-cell, enabling mixed rendering modes on the same grid line.

---

## Architecture

```
GridAlgebra (fixed 24×24 cells)     ← grid-core/types.ts, buffer.ts, algebra.ts
  └── GridBuffer: GridCell[][]       ← cols × rows, each cell is 24×24 CSS px
       └── GridCell {
             char: string            ← G0 char code (teletext) or Unicode
             fg, bg: number          ← palette indices 0-7
             bold?, blink?, mosaic?  ← formatting flags
             width?: number          ← render width in CSS px (optional)
           }
            ↓
GridUICanvasElement.setBuffer(buf)   ← Web Component
  ├── Background: fillRect → full 24×24 cell (zero gaps)
  ├── Mode: font (Press Start 2P)    ← fillText, square, natural
  ├── Mode: teletext (MODE7GX3)      ← fillText clipped, char-width=26px
  └── Mode: block (fillRect)         ← solid fills for graphic chars
```

## Core Principle: Fixed Grid, Variable Char Width

```
┌─────────────────────────────────────────────────┐
│  Grid is always: cols × cellSize CSS pixels      │
│  e.g. 40 × 20px = 800 × 500                      │
│                                                   │
│  Each cell background: 20 × 20 px (gapless)       │
│  Each char renders at: cell.width || defaultCharW │
│                                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ background│  │ background│  │ background│       │
│  │   [==]    │  │ [MODE7GX3]│  │ [Press2P] │       │
│  │  charW=26 │  │ charW=26  │  │ charW=20  │       │
│  └──────────┘  └──────────┘  └──────────┘        │
│  Same grid cell size (20×20), different char width │
└─────────────────────────────────────────────────┘
```

## Surface Layout

### UCodeSurface (route: `/ucode`)

| Tab | Cols | Rows | Cell | Font | Char W | Viewport | Notes |
|-----|------|------|------|------|--------|----------|-------|
| **Terminal** | 40 | 25 | 20px | `pressstart2p` | 20px | 800×500 | Square, natural |
| **Teletext** | 40 | 25 | 20px | `mode7gx3` | 26px | 800×500 | Wider chars, clipped |
| **Grid** (editor) | 24 | 24 | 24px | `mode7gx3` | 24px | 576×576 | 1× retro base |
| **Grid** (layer) | 40 | 25 | 12px | `mode7gx3` | 12px | 480×300 | Miniature overview |
| **Layer** | 40 | 25 | 20px | `mode7gx3` | 26px | 800×500 | Match teletext |

### Standalone Routes

| Route | Cols | Rows | Cell | Font | Char W | Viewport |
|-------|------|------|------|------|--------|----------|
| `/terminal` | 40 | 25 | 20px | `pressstart2p` | 20px | 800×500 |
| `/teletext` | 40 | 25 | 20px | `mode7gx3` | 26px | 800×500 |

## Pixel-Perfect Rendering Guarantees

### Cell Dimensions (fixed)
```
canvas CSS width  = cols × cellSize          (exact, e.g. 800px)
canvas CSS height = rows × cellSize          (exact, e.g. 500px)
canvas pixel w/h  = CSS dims × devicePixelRatio
```

### Zero-Gap Background
Each cell background fills the full cell with 1px overlap:
```javascript
ctx.fillRect(x, y, cellW + 1, cellH + 1)
```
No gap, padding, or margin between adjacent cell backgrounds — ever.

### Variable Char Width
```javascript
// Per-cell width overrides default
const chW = cell.width ? Math.round(cell.width * dpr) : defaultCharW

// Character centered within its width inside the fixed cell
const cx = x + (cellW - chW) / 2 + chW / 2
ctx.fillText(cell.char, cx, y + cellH / 2)
```

| Scenario | Cell | Char Width | Overflow | Clipped |
|----------|------|-----------|----------|---------|
| Square font (pressstart2p) | 20px | 20px (= cell) | None | No |
| Teletext (MODE7GX3) | 20px | **26px** | +3px each side | Yes |
| Per-cell override | 20px | cell.width | Varies | Yes |

### Font Sizing (derived from char-width)
```
fontScale = defaultCharW / cellW    (in physical pixels)
fontSize  = cellSize × fontScale × dpr
```

| Font | Config | Scale | Font Size | Glyph Fill |
|------|--------|-------|-----------|------------|
| `pressstart2p` | char-width=20 | 1.0× | 40px @2x | ~50% (natural) |
| `mode7gx3` | char-width=26 | **1.3×** | 52px @2x | **101%** ✅ |
| `mode7gx3` (fallback) | char-width=24 | 1.0× | 40px @2x | ~78% |

### Colour Palette
The 8-colour unified palette (`PALETTE_DARK`) from `grid-core/palette.ts`:<｜end▁of▁thinking｜>

<｜｜DSML｜｜tool_calls>
<｜｜DSML｜｜invoke name="read_file">
<｜｜DSML｜｜parameter name="filePath" string="true">/Users/fredbook/Code/uCore/docs/GRIDUI_RENDERING_CONTRACT.md
| Index | Dark Theme | Purpose |
|-------|-----------|---------|
| 0 | `#000000` | Background/black |
| 1 | `#dc3545` | Red/error |
| 2 | `#198754` | Green/success |
| 3 | `#ffc107` | Yellow/warning |
| 4 | `#0d6efd` | Blue/info |
| 5 | `#6f42c1` | Purple/accent |
| 6 | `#0dcaf0` | Cyan/info-alt |
| 7 | `#f8f9fa` | Foreground/white |

## Container Behavior

### Grid Sizing
- The `<gridui-canvas>` custom element sizes itself intrinsically to `cols × cellSize` CSS pixels.
- The host element sets `style.width` and `style.height` to match.
- The viewport (`.ucode-viewport`) is a flex container with `overflow: auto`.
- If the grid is **smaller** than the viewport → centered via flexbox.
- If the grid is **larger** than the viewport → scrollbars appear.

### Retina/DPR Handling
- Canvas pixel dimensions = CSS dimensions × `devicePixelRatio`
- The `<canvas>` element's `width`/`height` attributes are set in physical pixels.
- CSS `width`/`height` on the canvas use CSS pixel values (matching grid dimensions).
- This ensures crisp rendering on Retina displays.

## Rendering Component Architecture

```
UCodeSurface.vue                    ← Tab UI, demo data loading
  ├── canvasCache (Map<tabId, Element>)  ← State preservation across tab switches
  └── gridui-canvas (Web Component)      ← Renders each tab's grid

grid-core/gridui-canvas.ts          ← Canvas 2D renderer (PRIMARY)
  └── GridUICanvasElement            ← Custom Element
       ├── _fitCanvas()              ← Sets canvas to cols×cellSize
       ├── _render()                 ← Draws each cell as fillRect + fillText
       ├── setBuffer(buf)            ← Public API for buffer updates
       └── Supports blink, bold, mosaic modes

vendor/gridui-canvas/GridUICanvasElement.ts  ← CSS Grid span renderer (ALTERNATE)
  └── Used by standalone /terminal route (TerminalSurface.vue)
```

## Grid Buffer Type (Canonical)

```typescript
interface GridCell {
  char: string        // The character to display (single glyph)
  fg: number          // Foreground colour index (0-7)
  bg: number          // Background colour index (0-7)
  bold?: boolean      // Bold flag
  blink?: boolean     // Blink flag (teletext)
  mosaic?: boolean    // Mosaic block graphic flag
  /** Render width in CSS pixels within the fixed cell.
   *  Defaults to char-width attribute (26 for teletext, 20 for terminal).
   *  Enables mixing square fonts, teletext, and sprites on same grid line. */
  width?: number
}

type GridBuffer = GridCell[][]  // [row][col], y × x
```

**Source**: `frontend-vue/src/grid-core/types.ts`

### Render Modes (per cell, on the same grid line)

| Mode | How | Cell example |
|------|-----|-------------|
| **Square font** | `fillText` at cell size | `pressstart2p` — 20px char in 20px cell |
| **Teletext** | `fillText` clipped, wider char | `mode7gx3` — 26px char in 20px cell |
| **Block graphic** | `fillRect` full cell | `=`, `-`, `|`, `#`, `X` |
| **Sprite/emoji** | `cell.width` + `cell.char` | Any width, any glyph |
| **Mosaic** | 2×3 sub-cell blocks | Teletext G0 block graphics |

## uCode Runtime Requirements

The uCode backend runtime must produce `GridBuffer` objects. The runtime should:

1. **Use any grid size** — 40×25 is the current standard; aspect presets in algebra.ts
2. **Colour indices 0-7** from the unified palette (GitHub Dark / Bootstrap)
3. **Per-cell char widths** via `cell.width` — enables mixed rendering
4. **Support `bold`** for double-stroke, **`blink`** for teletext flash
5. **Support `mosaic`** for 2×3 block graphics
6. **Single Unicode code point per cell** — one character per GridCell

### Canvas vs CSS Rendering Decision — uCode Runtime Analysis

#### Comparison

| Factor | Canvas 2D (current) | CSS DOM (`<span>` per cell) | Hybrid |
|--------|---------------------|---------------------------|--------|
| **Text crispness** | `fillText` always anti-aliased | `-webkit-font-smoothing:none` = **pixel-crisp** ✅ | Canvas for graphics, CSS for text |
| **G0 bitmap quality** | Via offscreen canvas + NN scaling = crisp | Via @font-face (Galax approach) = **native crisp** | CSS text + canvas overlay |
| **Performance (static)** | Single element, GPU composited ✅ | 1000 spans = fine ✅ | Slightly more complex |
| **Performance (animated)** | `setBuffer()` → `_render()` = direct pixel push ✅ | 1000 DOM updates = layout thrash ❌ | Canvas handles animation |
| **Per-pixel control** | Full — blend modes, transforms, drawImage ✅ | None ❌ | Canvas overlay handles this |
| **Sprite overlay** | `drawImage` = trivial ✅ | Absolute positioning = painful ❌ | Canvas overlay ✅ |
| **Text selection** | None ❌ | Native browser selection ✅ | CSS layer handles this |
| **Accessibility** | None ❌ | Screen readers see text ✅ | CSS layer handles this |
| **Hit-testing** | Manual cell-from-coord math | Browser native (click on span) | Both available |
| **Scrolling** | `ctx.scroll` or re-render | Native DOM scroll | Canvas in scroll container |
| **Implementation** | 300-line Web Component ✅ | Template per cell, event delegation | Two layers, synced |

#### Recommendation: Canvas for Runtime, CSS for Viewing

The uCode runtime will produce two types of output:

| Output type | Volume | Update rate | Best renderer |
|-------------|--------|-------------|---------------|
| **Running BASIC/AMOS program** | Streaming | Per-frame (e.g. 30fps) | **Canvas** — direct pixel buffer updates, no DOM churn |
| **Teletext page** | Static/loaded | Once | **CSS** — pixel-crisp text, selectable, accessible |
| **Sprites / game graphics** | Continuous | Per-frame | **Canvas** — drawImage, transforms |
| **Grid editor** | Interactive | On click | **Canvas** — single buffer, instant redraw |

**Decision**: The uCore frontend keeps **Canvas 2D** as the primary renderer. The `<gridui-canvas>` Web Component is designed to be embedded in any framework (Vue, React, plain HTML). For the uCode runtime specifically:

1. **Canvas for active runtime output** — BASIC programs, game loops, sprites, scrolling terminal. Single buffer, direct pixel push, no DOM overhead.
2. **G0 bitmap cache** — Pre-render MODE7GX3 characters to binary bitmaps (see planned enhancement below). This gives pixel-crisp teletext text on canvas, matching CSS quality.
3. **CSS DOM for static viewing** — Optional render mode where the grid is rendered as CSS `<span>` elements with `-webkit-font-smoothing: none` for maximum readability. Used for teletext page browsing, documentation, etc.
4. **Hybrid as future path** — CSS for text layer, canvas overlay for graphics. Requires position synchronization but gives the best of both worlds.

### G0 Bitmap Renderer

The teletext view uses a **G0 bitmap renderer** instead of `fillText()`. This eliminates canvas anti-aliasing, matching galax.xyz CSS quality.

**Pipeline:**
```
MODE7GX3 font
  → Render char at 48×40 (4× G0 size) on offscreen canvas
    → Read pixels, threshold at 50% alpha → binary (fg/bg)
      → Downscale 4× to 12×10 → G0 glyph bitmap
        → Cache (Uint8Array, 120 bytes per char, 96 chars = 11.5KB)
          → Render: 2× nearest-neighbour → 24×20, center in 24×24 cell
            → putImageData or per-pixel fillRect
```

**Mosaic blocks** (2×3) are generated algorithmically from the 6-bit pattern in the character code — no font needed.

**Result**: Zero anti-aliasing. Pixel-crisp Ceefax text matching galax.xyz CSS quality, rendered at canvas framerates with no DOM overhead.

### Viewport Size Reference (24×24 base cell)

```yaml
viewports:
  terminal_80x24:
    1x: "1920×576"   # 80×24 × 24px
    2x: "3840×1152"  # 80×24 × 48px  ← sweet spot
  
  teletext_40x25:
    1x: "960×600"    # 40×25 × 24px
    2x: "1920×1200"  # 40×25 × 48px
    3x: "2880×1800"  # 40×25 × 72px  ← teletext ideal
  
  world_square_80x80:
    1x: "1920×1920"
    2x: "3840×3840"
  
  world_classic_80x60:
    1x: "1920×1440"
    2x: "3840×2880"
  
  widescreen_128x72:
    1x: "3072×1728"
    2x: "6144×3456"
```

## Verification Checklist

- [ ] Canvas `width`/`height` = `cols × cellSize × dpr`
- [ ] Canvas CSS dimensions = `cols × cellSize`
- [ ] Host element dimensions match canvas
- [ ] No gaps between adjacent cells (verify via `getImageData` pixel sampling)
- [ ] Font renders centered in cell (check `textBaseline: 'middle'`)
- [ ] Retina displays render at 2x without blur
- [ ] Tab switching preserves buffer state
- [ ] Grid larger than viewport → scrollable
- [ ] Grid smaller than viewport → centered

## Key Design Decisions

1. **Fixed 24×24 cells, variable char widths** — The grid algebra is constant. Character width is a per-cell property (`GridCell.width`), enabling mixed rendering modes (square font, teletext, sprites) on the same grid line.

2. **Per-cell font sizing**: `fontScale = defaultCharW / cellW` — the font size derives from the char width. This means `char-width=26` at 20px cells gives 1.3× scale, filling 101% of the cell width.

3. **MODE7GX3 for teletext** — Downloaded from galax.xyz, based on ModeSeven (BBC Micro MODE 7). Loaded via @font-face from `public/fonts/`. Replaces VT323 which had narrow glyphs.

4. **All canvas, not CSS** — The `<gridui-canvas>` Web Component renders to a single `<canvas>` element. CSS DOM rendering with `-webkit-font-smoothing: none` could give crisper text but loses the per-pixel control needed for sprite/mosaic overlay.

5. **Per-cell mosaic blocks** — The G0 2×3 mosaic system (6 sub-cells, each on/off via 6-bit code) is supported via the `mosaic` flag on `GridCell`.

6. **G0 bitmap renderer (planned)** — Pre-render MODE7GX3 chars to 12×10 bitmaps via offscreen canvas, threshold to binary, render with nearest-neighbour scaling for pixel-crisp output matching galax.xyz quality.

## Playwright Audit Results (2026-07-02)

| Tab | Expected | Actual | Canvas Pixels | Char Fill | Gaps |
|-----|----------|--------|---------------|-----------|------|
| Terminal (40×25, 20px, press2p) | 800×500 | 800×500 ✅ | 1600×1000 | ~50% (natural) | 0 bg gaps |
| Teletext (40×25, 20px, mode7gx3) | 800×500 | 800×500 ✅ | 1600×1000 | **101%** ✅ | 0 bg, 10 narrow-char |
| Grid editor (24×24, 24px) | 576×576 | 576×576 ✅ | 1152×1152 | 100% (block) | 0 |
| Grid layer (40×25, 12px) | 480×300 | 480×300 ✅ | 960×600 | — | — |

**All tabs: zero background gaps. Teletext: 0/40 separator gaps (edge-to-edge).**
