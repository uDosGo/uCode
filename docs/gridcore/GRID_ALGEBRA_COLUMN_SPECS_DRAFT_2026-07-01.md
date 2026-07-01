# Grid Algebra & Column Size Specs

> **Status:** Draft  
> **Date:** 2026-07-01  
> **Scope:** Grid Algebra, Column Size Specs, View Transformation Pipeline, GridCoreUI, Prose UI

---

## 1. Philosophy

The Grid Algebra is the mathematical foundation that unifies all display modes in uCore. It defines:

1. **Column sizes** — how character width relates to viewport dimensions
2. **Grid buffers** — the canonical data structure for character-based displays
3. **Viewport transforms** — how a grid buffer maps to different screen sizes
4. **View transformations** — how markdown content maps to different output formats

### Two Display Families

| Family | Purpose | Examples | Rendering |
|--------|---------|----------|-----------|
| **GridCore UI** | Embeddable character-grid widgets | Terminal, Teletext, Grid Editor | `<gridui-canvas>` Web Component |
| **Prose UI** | Text/content browsers | Web pages, Publishing, Docs | HTML + CSS layout |

Both families share:
- Google CDN fonts (Inter for prose, VT323/PressStart2P for grid)
- USX design tokens for spacing and color
- The Grid Algebra for dimension calculations

---

## 2. Column Size Specs

### 2.1 Character-to-Column Relationship

The fundamental unit is the **character cell** — a monospace character at a given font size. Column width is measured in `ch` units (CSS `ch` = width of `0` character in the current font).

| Token | Value | Description |
|-------|-------|-------------|
| `--usx-col-width-xs` | 40ch | Narrow single column |
| `--usx-col-width-sm` | 35ch | Comfortable reading column |
| `--usx-col-width-md` | 72ch | Standard prose width (existing) |
| `--usx-col-width-lg` | 80ch | Wide reading column |
| `--usx-col-gap` | 24px | Gap between columns |

### 2.2 Viewport Column Presets

| Viewport | Breakpoint | Columns | Column Width | Total Content Width | Use Case |
|----------|-----------|---------|-------------|-------------------|----------|
| **XS** | < 480px | 1 | 40ch (fluid) | 100% - 48px padding | Phone portrait |
| **SM** | 480-768px | 1-2 | 35ch | 100% - 48px padding | Phone landscape, small tablet |
| **MD** | 768-1024px | 2 | 35ch | ~700-900px | Tablet portrait |
| **LG** | 1024-1440px | 2-3 | 35ch | ~960-1280px | Desktop |
| **XL** | 1440-1920px | 3-4 | 35ch | ~1280-1600px | Large monitor |
| **XXL** | 1920px+ | 4-6 | 30ch | ~1600-1920px | TV, projector, ultrawide |

### 2.3 Grid Character Presets

These define the character-cell grid dimensions for GridCore UIs:

| Grid Mode | Cols | Rows | Aspect | Use Case |
|-----------|------|------|--------|----------|
| **Teletext** | 40 | 25 | 4:3 | Classic Ceefax/Teletext |
| **Teletext Wide** | 48 | 36 | 4:3 | Extended teletext (backend default) |
| **Terminal** | 80 | 24 | ~4:3 | Classic terminal |
| **Terminal Wide** | 120 | 36 | 16:9 | Wide terminal |
| **GridCore Editor** | 60 | 20 | 3:1 | Grid editing workspace |
| **GridCore Map** | 60 | 20 | 3:1 | Map/grid view |
| **Mini** | 28 | 28 | 1:1 | Square widget |

### 2.4 CSS Custom Properties

```css
:root {
  /* Column width tokens */
  --usx-col-width-xs: 40ch;
  --usx-col-width-sm: 35ch;
  --usx-col-width-md: 72ch;
  --usx-col-width-lg: 80ch;
  --usx-col-gap: 24px;

  /* Column count per breakpoint */
  --usx-cols-xs: 1;
  --usx-cols-sm: 1;
  --usx-cols-md: 2;
  --usx-cols-lg: 3;
  --usx-cols-xl: 4;
  --usx-cols-xxl: 6;

  /* Grid character presets */
  --usx-grid-teletext: 40x25;
  --usx-grid-teletext-wide: 48x36;
  --usx-grid-terminal: 80x24;
  --usx-grid-terminal-wide: 120x36;
  --usx-grid-editor: 60x20;
}
```

---

## 3. Grid Algebra

### 3.1 Core Types

```typescript
/** A single cell in a grid buffer */
interface GridCell {
  char: string        // The character to display
  fg: number          // Foreground colour index (0-7)
  bg: number          // Background colour index (0-7)
  bold?: boolean      // Bold flag
  blink?: boolean     // Blink flag (teletext)
  mosaic?: boolean    // Mosaic block graphic flag
}

/** A 2D grid buffer */
type GridBuffer = GridCell[][]

/** Viewport dimensions */
interface Viewport {
  cols: number        // Number of character columns
  rows: number        // Number of character rows
  cellWidth: number   // Pixel width of each cell
  cellHeight: number  // Pixel height of each cell
  font: string        // Font family name
}

/** Column specification for prose layouts */
interface ColumnSpec {
  count: number       // Number of columns
  width: string       // CSS width value (e.g. "35ch")
  gap: string         // CSS gap value (e.g. "24px")
  breakpoint: number  // Min viewport width in px
}
```

### 3.2 Viewport Resolution

```typescript
/**
 * Resolve the optimal column spec for a given viewport width.
 */
function resolveColumns(viewportWidth: number): ColumnSpec {
  if (viewportWidth >= 1920) return { count: 6, width: '30ch', gap: '24px', breakpoint: 1920 }
  if (viewportWidth >= 1440) return { count: 4, width: '35ch', gap: '24px', breakpoint: 1440 }
  if (viewportWidth >= 1024) return { count: 3, width: '35ch', gap: '24px', breakpoint: 1024 }
  if (viewportWidth >= 768)  return { count: 2, width: '35ch', gap: '24px', breakpoint: 768 }
  if (viewportWidth >= 480)  return { count: 2, width: '35ch', gap: '16px', breakpoint: 480 }
  return { count: 1, width: '40ch', gap: '0', breakpoint: 0 }
}

/**
 * Calculate pixel dimensions for a character grid viewport.
 */
function calcViewport(cols: number, rows: number, cellSize: number, font: string): Viewport {
  return {
    cols,
    rows,
    cellWidth: cellSize,
    cellHeight: cellSize * 1.2, // typical character height-to-width ratio
    font,
  }
}
```

### 3.3 Grid Buffer Operations

```typescript
/** Create an empty grid buffer */
function createBuffer(cols: number, rows: number): GridBuffer

/** Write a string into the buffer at position */
function writeString(
  buf: GridBuffer,
  col: number,
  row: number,
  text: string,
  fg?: number,
  bg?: number,
  bold?: boolean
): GridBuffer

/** Fill a rectangular region */
function fill(
  buf: GridBuffer,
  col: number,
  row: number,
  width: number,
  height: number,
  char: string,
  fg?: number,
  bg?: number
): GridBuffer

/** Scroll buffer up by n rows */
function scroll(buf: GridBuffer, rows?: number): GridBuffer

/** Clear the buffer */
function clear(buf: GridBuffer): GridBuffer
```

### 3.4 Viewport Transforms

```typescript
/** Scale a grid buffer to a new dimension (nearest-neighbour) */
function scaleBuffer(buf: GridBuffer, newCols: number, newRows: number): GridBuffer

/** Crop a grid buffer to a sub-region */
function crop(buf: GridBuffer, col: number, row: number, width: number, height: number): GridBuffer

/** Centre a grid buffer within a larger viewport */
function centre(buf: GridBuffer, canvasCols: number, canvasRows: number): GridBuffer
```

---

## 4. View Transformation Pipeline

### 4.1 Markdown → Multi-View Pipeline

```
                    ┌──────────────────┐
                    │   Markdown Source │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │  Parse Frontmatter│
                    │  + Split on ---  │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
     ┌────────▼──────┐ ┌────▼──────┐ ┌─────▼──────┐
     │  Prose View   │ │Slide View │ │Multi-Col   │
     │ (standard     │ │(Marp)     │ │View        │
     │  scroll)      │ │           │ │            │
     └───────────────┘ └───────────┘ └────────────┘
              │              │              │
     ┌────────▼──────┐ ┌────▼──────┐ ┌─────▼──────┐
     │  Web Pub      │ │Print/PDF  │ │GridCore    │
     │  (responsive  │ │(stub)     │ │Embed       │
     │   columns)    │ │           │ │            │
     └───────────────┘ └───────────┘ └────────────┘
```

### 4.2 Slide Separator Convention

- `---` (horizontal rule) on its own line = **slide separator** in Marp mode
- `---` is **removed** from Prose rendering (invisible in scroll view)
- `---` is **invisible marker** for story/broken-up pages
- Frontmatter (YAML between `---` delimiters at start) provides slide/page metadata

### 4.3 Rendering Modes

| Mode | Renderer | Output | Notes |
|------|----------|--------|-------|
| **prose** | `useMarkdown.ts` (enhanced) | HTML | Standard scroll, `---` removed |
| **columns** | `MultiColumnViewer.vue` | CSS columns | Content flows into columns |
| **slides** | `@marp-team/marp-core` | HTML slides | `---` = slide break |
| **web-pub** | `PublishViewer.vue` | HTML + CSS | Responsive columns, web fonts |
| **grid** | `<gridui-canvas>` | Canvas/WebGL | Character grid rendering |

---

## 5. GridCoreUI Embeddable Component

### 5.1 Component Interface

```vue
<GridCoreUI
  :buffer="gridBuffer"
  :cols="60"
  :rows="20"
  :cell-size="16"
  :font="'pressstart2p'"
  :mode="'edit' | 'view' | 'map'"
/>
```

### 5.2 Web Component (`<gridui-canvas>`)

Framework-agnostic custom element that:
- Renders a character grid to a `<canvas>` element
- Supports colour palette (8 foreground + 8 background)
- Handles bold, blink, mosaic modes
- Auto-scales to fit container
- Emits `cell-click` and `cell-hover` events

### 5.3 Colour Palette

| Index | Name | Hex (Dark) | Hex (Light) |
|-------|------|-----------|------------|
| 0 | Black | `#000000` | `#000000` |
| 1 | Red | `#e6193c` | `#cc0000` |
| 2 | Green | `#3fb950` | `#00aa00` |
| 3 | Yellow | `#f2cc60` | `#cccc00` |
| 4 | Blue | `#58a6ff` | `#0000cc` |
| 5 | Magenta | `#bc8cff` | `#cc00cc` |
| 6 | Cyan | `#39c5cf` | `#00cccc` |
| 7 | White | `#c9d1d9` | `#ffffff` |

---

## 6. USX CSS Extensions

### 6.1 New Tokens

```css
:root {
  /* Column widths */
  --usx-col-width-xs: 40ch;
  --usx-col-width-sm: 35ch;
  --usx-col-width-md: 72ch;
  --usx-col-width-lg: 80ch;
  --usx-col-gap: 24px;

  /* Prose width variants */
  --usx-prose-width-sm: 40ch;
  --usx-prose-width-md: 72ch;
  --usx-prose-width-lg: 80ch;
}
```

### 6.2 Column Classes

```css
/* Multi-column layout */
.usx-columns { column-gap: var(--usx-col-gap); }
.usx-columns-1 { columns: 1; }
.usx-columns-2 { columns: 2; }
.usx-columns-3 { columns: 3; }
.usx-columns-4 { columns: 4; }
.usx-columns-6 { columns: 6; }

/* Responsive columns */
.usx-columns--responsive {
  columns: 1;
}
@media (min-width: 480px) { .usx-columns--responsive { columns: var(--usx-cols-sm); } }
@media (min-width: 768px) { .usx-columns--responsive { columns: var(--usx-cols-md); } }
@media (min-width: 1024px) { .usx-columns--responsive { columns: var(--usx-cols-lg); } }
@media (min-width: 1440px) { .usx-columns--responsive { columns: var(--usx-cols-xl); } }
@media (min-width: 1920px) { .usx-columns--responsive { columns: var(--usx-cols-xxl); } }
```

### 6.3 Prose Width Variants

```css
.usx-prose--sm { max-width: var(--usx-prose-width-sm); }
.usx-prose--md { max-width: var(--usx-prose-width-md); }
.usx-prose--lg { max-width: var(--usx-prose-width-lg); }
```

---

## 7. Implementation Roadmap

### Phase 1: Spec + CSS Primitives (NOW)
- [x] This spec document
- [ ] Add column tokens to `usx-standard.css`
- [ ] Add column classes to `usx-standard.css`
- [ ] Add prose width variants

### Phase 2: Grid Algebra Package
- [ ] Create `frontend-vue/src/grid-core/algebra.ts`
- [ ] Create `frontend-vue/src/grid-core/viewport.ts`
- [ ] Create `frontend-vue/src/grid-core/buffer.ts`
- [ ] Create `frontend-vue/src/grid-core/types.ts`
- [ ] Create `frontend-vue/src/grid-core/index.ts`

### Phase 3: GridCoreUI Web Component
- [ ] Create `<gridui-canvas>` custom element
- [ ] Fix cell spacing (no gaps between tiles)
- [ ] Implement colour palette
- [ ] Implement bold/blink/mosaic modes
- [ ] Implement auto-scale to container

### Phase 4: Markdown Enhancement
- [ ] Update `useMarkdown.ts` to strip `---` in prose mode
- [ ] Add Marp slide rendering pipeline
- [ ] Create `MultiColumnViewer.vue`
- [ ] Create `SlideViewer.vue`
- [ ] Create `PublishViewer.vue`

### Phase 5: GridCoreUI Vue Component
- [ ] Create `GridCoreUI.vue` wrapper
- [ ] Integrate with grid algebra
- [ ] Support mode switching (edit/view/map)

### Phase 6: Prose UI Viewers
- [ ] Create `ProseViewer.vue`
- [ ] Wire up to existing surfaces
- [ ] Add web publishing layout
