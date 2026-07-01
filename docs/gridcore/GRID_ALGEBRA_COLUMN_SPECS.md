# Grid Algebra — Column Width & Viewport Spec

> **Status:** ✅ Finalised (v2.0)  
> **Supersedes:** v1.x (archived below)  
> **Last Updated:** 2026-01-07

---

## 1. Core Principle: Character Density Guarantee

**Character count per column MUST increase with viewport size, never decrease.**  
This ensures readable content at all sizes — small viewports get fewer, wider columns; large viewports get more, narrower columns with the same per-column character density.

---

## 2. Column Spec Table

| Viewport Width | Column Count | Per-Column Width | Gap    | Alias        |
|---------------|-------------|------------------|--------|--------------|
| < 480px       | 1           | 40ch             | 0      | `xs`         |
| 480–768px     | 2           | 35ch             | 16px   | `sm`         |
| 768–1024px    | 2           | 40ch             | 24px   | `md`         |
| 1024–1440px   | 3           | 35ch             | 24px   | `lg`         |
| 1440–1920px   | 3           | 40ch             | 24px   | `xl`         |
| 1920px+       | 4           | 40ch              | 24px   | `xxl`        |

### Rationale

- **1×40ch (xs):** Single-column reading on phones. 40ch ≈ 8–10 words/line, optimal for narrow viewports.
- **2×35ch (sm):** Two compact columns on tablets. 35ch ≈ 7–9 words/line.
- **2×40ch (md):** Two wider columns on landscape tablets. 40ch ≈ optimal reading width.
- **3×35ch (lg):** Three columns on desktop browsers. 35ch keeps lines short enough for comfortable reading.
- **3×40ch (xl):** Three wider columns on large desktop. Full reading width.
- **4×40ch (xxl):** Four columns on ultrawide/TV. Cinema/boardroom display mode.

---

## 3. Design Tokens (CSS Custom Properties)

These are the source-of-truth tokens, defined in `usx-standard.css`:

```css
/* Column Width Tokens */
--usx-col-width-xs: 40ch;
--usx-col-width-sm: 35ch;
--usx-col-width-md: 72ch;   /* single-column prose reading */
--usx-col-width-lg: 80ch;   /* single-column prose wide */
--usx-col-gap: 24px;

/* Column Count Per Breakpoint */
--usx-cols-xs: 1;    /* < 480px  */
--usx-cols-sm: 2;    /* 480px+   */
--usx-cols-md: 2;    /* 768px+   */
--usx-cols-lg: 3;    /* 1024px+  */
--usx-cols-xl: 3;    /* 1440px+  */
--usx-cols-xxl: 4;   /* 1920px+  */
```

---

## 4. Grid Algebra Functions

```typescript
// src/grid-core/algebra.ts

resolveColumns(viewportWidth: number): ColumnSpec
// Returns { count, width, gap, breakpoint } for the current viewport

resolveProseWidth(viewportWidth: number): string
// Returns optimal max-width string for single-column prose

columnSpecToMaxWidth(spec: ColumnSpec): string
// Converts spec to CSS max-width value

columnSpecTotalWidth(spec: ColumnSpec): string
// Calculates total content width (columns + gaps) as CSS calc()
```

---

## 5. Viewer Modes & Column Behaviours

### ProseViewer (`ProseViewer.vue`)
- **Purpose:** Traditional scrolling document reading  
- **Column behaviour:** Auto-resolves via `resolveColumns()`, sets responsive `max-width`  
- **Single-column:** `1×40ch` centred  
- **Multi-column:** Uses CSS `columns` property, width calculated from spec  
- **Slide separators:** Automatically stripped  

### MultiColumnViewer (`MultiColumnViewer.vue`)
- **Purpose:** Newspaper/magazine grid layout  
- **Column behaviour:** Auto-resolves via `resolveColumns()`, uses CSS Grid with `grid-template-columns`  
- **Each column:** Wrapped in card-style container with border and background  
- **Column count:** 1–4 based on viewport  

### SlideViewer (`SlideViewer.vue`)
- **Purpose:** Marp-style presentation slides  
- **Column behaviour:** Single slide at a time, navigation controls  
- **Aspect ratios:** 16:9, 4:3, fill  
- **Width:** 960px max, responsive padding  

### GridCoreUI (`GridCoreUI.vue`)
- **Purpose:** Character-grid embeddable widget  
- **Column behaviour:** Fixed character grid (teletext/terminal style)  
- **Cell rendering:** Pixel-perfect `canvas` via `gridui-canvas.ts`  
- **Palette:** 8-colour foreground + background  

### Web Publishing View
- **Purpose:** Public web publishing (markdown → HTML)  
- **Column behaviour:** Same responsive spec as ProseViewer  
- **Options:** Full-width scroll, multi-column, or slide view  

---

## 6. Non-Column Design Standards

### UI Spacing (8px System)

| Token | Value | Usage |
|-------|-------|-------|
| `--usx-spacing-xs` | 4px | Micro margins |
| `--usx-spacing-sm` | 8px | Tight grouping |
| `--usx-spacing-md` | 12px | Buttons, inputs |
| `--usx-spacing-lg` | 16px | Cards, sections |
| `--usx-spacing-xl` | 24px | Page padding |
| `--usx-spacing-2xl` | 32px | Wide sections |

### Icon Standards (Material Symbols Outlined + Iconify)
- **Relative sizing:** `1em` default, `1.25em` for larger contexts, `1.5em` for headings  
- **Icon+label gap:** `0.5em` (Material3 standard)  
- **Minimum touch target:** 32×32px for icon-only buttons  
- **No hardcoded px:** All icon sizes use em/rem relative to context  
- **No `!important`:** Use specificity cascade instead  

### Form/Button Standards (Pico-sized, mobile-friendly)
- **Button height:** 40px default, 44px for large touch targets  
- **Button padding:** 8px vertical, 16px horizontal  
- **Input height:** 40px default, 32px compact, 44px large  
- **Hit area:** Minimum 44×44px on mobile  

### Color & Border Standards (GitHub-inspired dark)
- **Background:** `#0d1117` (pico surface)  
- **Card background:** `#141b26`  
- **Border:** `rgba(88, 166, 255, 0.08)` or `#30363d`  
- **Primary accent:** `#58a6ff`  
- **Code block background:** `#1a2332`  
- **No fades, shading, color-blending, or animation** — flat, minimal borders  
- **Focus indicator:** 1px `#58a6ff` outline (focus-visible only)  

### Typography
- **Body:** Inter, system-ui, 1rem (16px), line-height 1.6  
- **Monospace:** Menlo, Monaco, Courier New  
- **Headings:** 600 weight, tight line-height (1.3)  
- **Prose line-height:** 1.8 for relaxed reading  

---

## 7. Grid Presets (Character Grids)

| Preset | Cols | Rows | Aspect | Use Case |
|--------|------|------|--------|----------|
| teletext | 40 | 25 | 4:3 | Classic Ceefax/Teletext |
| teletext-wide | 48 | 36 | 4:3 | Extended teletext |
| terminal | 80 | 24 | 4:3 | Classic terminal |
| terminal-wide | 120 | 36 | 16:9 | Wide terminal |
| editor | 60 | 20 | 3:1 | Grid editing workspace |
| map | 60 | 20 | 3:1 | Map/grid view |
| mini | 28 | 28 | 1:1 | Square widget |

---

## 8. Archived Spec (v1.x)

### Previous Column Spec (v1.0, deprecated)

| Viewport | Cols | Width | Notes |
|----------|------|-------|-------|
| < 480px | 1 | 100% | Full-width, no constraint |
| 480px+ | 1 | 40ch | Centred single column |
| 768px+ | 2 | 35ch | Two columns |
| 1024px+ | 2 | 40ch | Wider columns |
| 1440px+ | 3 | 35ch | Three narrower |

**Problems with v1.0:**
- No 4-column option for ultrawide/TV
- Inconsistent character density (2×40ch had more chars than 3×35ch but fewer columns)
- v1 used `72ch` prose width which was too wide for comfortable reading
- No CSS custom properties — hardcoded values everywhere

### Migration Notes
- All components updated to use `resolveColumns()` instead of hardcoded widths
- CSS custom properties now match the algebra spec exactly
- Viewers auto-resolve on window resize
- Barrel exports include all new algebra functions
- All `!important` declarations removed from Vue components
