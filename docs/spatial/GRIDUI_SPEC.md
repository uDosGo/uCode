---
title: "GridUI — Surface Specification"
status: draft
last_updated: 2026-06-11T20:58:00+10:00
category: specification
tags: [devstudio, grid, specification, ui]
description: "> **File:** `uConnect/ui/src/surfaces/gridui/`"
---
# GridUI — Surface Specification

> **File:** `uConnect/ui/src/surfaces/gridui/`
> **Styles:** `uConnect/ui/src/styles/gridui.css` (2268 lines) + `uConnect/ui/src/styles/surface-host.css` (USX token mappings)
> **Store:** `GridUIStore.ts` — React hook-based state management
> **Registration:** `UIHubManager.tsx` — core surface ID `'gridui'`, port 5178, icon `widgets`, color `#f0883e`
> **Project Type:** Technical (TC) | **Autonomy Level:** L4 (Delegator)
> **Tags:** `#grid #composer #layers #surface`
> **Last Updated:** 2026-06-11 (grid-algebra v1.0)

---

## 1. Architecture Overview

GridUI is a **USX Schema v3.1 Grid Layer Composer** — a retro-computing-inspired surface that provides a character-based grid system with layered overlays, a C64 BASIC terminal, document vault, dashboard, and settings panel. It's one of the core surfaces in the uConnect UI Hub, registered as the first surface in `CORE_SURFACE_IDS`.

### 1.1 Surface Registration (UIHubManager.tsx)

```typescript
{ id: 'gridui', name: 'uCode1', subtitle: 'Grid Layer Composer',
  description: 'Chat sheets, nav rails, teledesk panels, terminal, vault docs, and maps layers.',
  port: 5178, color: '#f0883e', icon: 'widgets', status: 'stopped',
  cell: 'L100-AA10-0101-1' }
```

### 1.2 File Structure

```
uConnect/ui/src/surfaces/gridui/
├── GridUISurface.tsx              # Main surface component — nav rail + panel router
├── GridUIStore.ts                 # State management — React hooks + localStorage persistence
├── grid-algebra/                  # Universal grid data model (NEW)
│   ├── GridCell.ts                # GridCell interface, GridBuffer type, factory functions
│   ├── GridTransform.ts           # Pure transform functions (resize, overlay, scroll, crop, merge)
│   ├── ColourPalette.ts           # Palette definitions (teletext, c64, ansi, modern, amber, green)
│   └── TeletextPage.ts            # Teletext page store + page builder (40×25 pages)
└── panels/
    ├── TerminalPanel.tsx          # C64 BASIC terminal (grid-algebra backed)
    ├── TeletextPanel.tsx          # Ceefax teletext page viewer (NEW)
    ├── DashboardPanel.tsx         # System stats, tasks, activity feed
    ├── VaultPanel.tsx             # Ceetex document viewer
    ├── GridEditorPanel.tsx        # Layer editor + character map
    ├── SettingsPanel.tsx          # Viewport, display, palette config
    ├── GridBufferRenderer.tsx     # Shared GridBuffer → DOM renderer (NEW)
    ├── GridWidget.tsx             # Embeddable grid renderer for any surface (NEW)
    └── SurfaceToolbar.tsx         # Viewport dropdown + nav keypad
```

---

## 2. State Management (GridUIStore.ts)

### 2.1 Core Types

```typescript
type GridPanelId = 'terminal' | 'teletext' | 'dashboard' | 'vault' | 'grid' | 'settings'
type Palette = 'modern' | 'c64' | 'teletext' | 'nes'
type FontStyle = 'serif' | 'sans' | 'mono'
type GridDisplayMode = 'teletext' | 'mono' | 'wireframe'
type BorderMode = 1 | 2 | 3
type ChatRole = 'user' | 'assistant' | 'system'
```

### 2.2 Panel Definitions

```typescript
PANELS: GridPanel[] = [
  { id: 'terminal',  label: 'Terminal',    icon: 'terminal',           description: 'C64 BASIC terminal' },
  { id: 'teletext',  label: 'Teletext',    icon: 'tv',                 description: 'Ceefax teletext page viewer' },
  { id: 'dashboard', label: 'Dashboard',   icon: 'speedometer2',       description: 'System stats & tasks' },
  { id: 'vault',     label: 'Vault',       icon: 'folder',             description: 'Ceetex document viewer' },
  { id: 'grid',      label: 'Grid Editor', icon: 'grid-3x3-gap-fill',  description: 'USX grid layers, cell editor & character maps' },
  { id: 'settings',  label: 'Settings',    icon: 'gear',               description: 'Styling & viewport configuration' },
]
```

### 2.3 Viewport Presets

```typescript
VIEWPORT_PRESETS: Record<string, ViewportSettings> = {
  '40x25': { cols: 40, rows: 25, zoom: 1, bgColor: '#000000', gridColor: '#21262d',
             textColor: '#00ff00', surfaceBgColor: '#000000', borderMode: 1, borderBgColor: '#000000' },
  '80x24': { cols: 80, rows: 24, zoom: 1, bgColor: '#0d1117', gridColor: '#21262d',
             textColor: '#e6edf3', surfaceBgColor: '#010409', borderMode: 1, borderBgColor: '#0d1117' },
  '60x24': { cols: 60, rows: 24, zoom: 1, bgColor: '#0d1117', gridColor: '#21262d',
             textColor: '#e6edf3', surfaceBgColor: '#010409', borderMode: 1, borderBgColor: '#0d1117' },
}
```

### 2.4 Border Mode Configs

```typescript
BORDER_MODE_CONFIGS: Record<BorderMode, { fillFraction: number; surfaceBg: string; borderBg: string }> = {
  1: { fillFraction: 0.80, surfaceBg: '#010409', borderBg: '#21262d' },  // Wide border
  2: { fillFraction: 0.90, surfaceBg: '#010409', borderBg: '#161b22' },  // Medium border
  3: { fillFraction: 0.98, surfaceBg: '#010409', borderBg: '#010409' },  // Borderless (full fill)
}
```

### 2.5 Character Dimensions

```typescript
CHAR_W = 9   // Character width in pixels
CHAR_H = 16  // Character height in pixels
```

### 2.6 Grid Layers (Default)

```typescript
gridLayers: GridLayer[] = [
  { id: 'layer-0', name: 'Base Grid',     visible: true,  zIndex: 0, color: '#1a1a1a', opacity: 1 },
  { id: 'layer-1', name: 'System Status',  visible: false, zIndex: 1, color: '#00FF00', opacity: 1 },
  { id: 'layer-2', name: 'Vault Contents', visible: false, zIndex: 2, color: '#00FFFF', opacity: 1 },
  { id: 'layer-3', name: 'Feed Items',     visible: false, zIndex: 3, color: '#FFFF00', opacity: 1 },
  { id: 'layer-4', name: 'QR Storage',     visible: false, zIndex: 4, color: '#FF00FF', opacity: 1 },
  { id: 'layer-5', name: 'Overlay',        visible: false, zIndex: 5, color: '#FF6600', opacity: 1 },
]
```

### 2.7 Persistence

All user preferences are persisted to `localStorage` under key `'gridui-prefs'`:
- `isDark`, `currentPalette`, `fontSize`, `fontStyle`, `viewport`, `navRailCollapsed`, `displayMode`

---

## 3. Surface Layout (GridUISurface.tsx)

### 3.1 Component Tree

```
GridUISurface
├── GridUIContext.Provider (store)
│   ├── GlobalToolbar (USX surface header — tabs, chat toggle, settings, sidebar)
│   ├── usx-surface-body
│   │   ├── usx-nav-rail (collapsible — 5 panel buttons + collapse toggle)
│   │   └── usx-surface-main
│   │       ├── {activePanel} (Terminal | Dashboard | Vault | GridEditor | Settings)
│   │       └── ViewportDropdown (floating bottom-right)
│   └── ChatSheet (fixed bottom-right overlay)
│   └── Snackbar (fixed bottom-center toast)
```

### 3.2 Nav Rail

- 5 panel buttons with Bootstrap Icons
- Collapsible via chevron button at bottom
- Active panel highlighted
- Each button has `title` attribute showing panel description

### 3.3 Chat Sheet

- Fixed position: bottom-right, 360px wide, 50vh tall
- Rounded top-left corner, shadow
- Message list with user/assistant styling
- Input field with Enter-to-send
- Simulated responses (800ms delay)
- Clear button, loading spinner

### 3.4 Snackbar

- Fixed bottom-center toast
- Color-coded by type: info (#58a6ff), success (#238636), warning (#d29922), error (#E76F51)
- Queue-based: shows one at a time, auto-dismiss after `duration` (default 4000ms)
- Optional action button

---

## 4. Panels

### 4.1 TerminalPanel — C64 BASIC Terminal (grid-algebra backed)

**File:** `panels/TerminalPanel.tsx`

A retro terminal emulator that simulates a Commodore 64 BASIC environment. Now uses `grid-algebra` internally — all display operations go through `GridBuffer` and `GridTransform`.

**Features:**
- Viewport-sized display: `width = cols × CHAR_W`, `height = rows × CHAR_H`
- Font: `'PetMe128','C64 User Mono','Courier New',monospace` at 16px
- Line-numbered input prompt (1, 2, 3...)
- Supported commands: `HELP/?`, `CLS/CLEAR`, `LIST`, `PRINT`, `TIME`, `DATE`, `WHOAMI`, `NEW`, `RUN`, `LOAD`, `SAVE`, `POKE`, `PEEK`, `SYS`, `EXIT/QUIT`
- Display mode filters: `mono` → grayscale(100%), `wireframe` → invert(100%) contrast(200%)
- Border mode controls viewport padding and background colors
- Auto-scroll to bottom on new output
- Input auto-focus on mount
- **Renders via `GridBufferRenderer`** — consistent cell rendering with TeletextPanel

### 4.2 TeletextPanel — Ceefax Teletext Page Viewer (NEW)

**File:** `panels/TeletextPanel.tsx`

A Ceefax-style teletext page viewer using `grid-algebra`. Pages are 40×25 `GridBuffer`s stored in `TeletextPageStore`.

**Features:**
- 3-digit page dialer (type a number to navigate)
- Built-in pages: Welcome (100), System Status (101), News (200), Colour Test Card (888)
- Palette switching (teletext, amber, green, modern)
- Viewport resize via `GridTransform.resize()`
- Keyboard shortcut: any digit key opens the page nav overlay
- Escape to dismiss nav overlay
- Page info bar showing current page number and title
- **Renders via `GridBufferRenderer`** — shared renderer with TerminalPanel

### 4.3 GridBufferRenderer — Shared GridBuffer → DOM Renderer (NEW)

**File:** `panels/GridBufferRenderer.tsx`

Pure component that renders a `GridBuffer` as a grid of character cells with proper foreground/background colours. Used by TerminalPanel, TeletextPanel, and GridWidget.

**Props:**
- `buffer: GridBuffer` — the grid data
- `paletteId: PaletteId` — colour palette to use
- `cellWidth?: number` — px per cell (default: 9)
- `cellHeight?: number` — px per cell (default: 16)

**Features:**
- Maps colour indices through the selected palette
- Supports bold, flash (blink animation), double-height, double-width flags
- Flash animation via CSS `@keyframes teletext-flash`

### 4.4 GridWidget — Embeddable Grid Renderer (NEW)

**File:** `panels/GridWidget.tsx`

A lightweight React component that renders a `GridBuffer` at any size. Can be embedded in ProseUI, Dashboard, or any other surface.

**Props:**
- `buffer: GridBuffer` — the grid data
- `paletteId?: PaletteId` — colour palette (default: 'modern')
- `width?: number` — px width (auto-fit if omitted)
- `height?: number` — px height (auto-fit if omitted)
- `className?: string` — CSS class
- `style?: React.CSSProperties` — inline styles

**Utility:**
- `textToGridBuffer(text, cols?)` — create a GridBuffer from plain text

### 4.5 DashboardPanel — System Stats & Tasks

**File:** `panels/DashboardPanel.tsx`

A 3-card dashboard with system stats, task management, and activity feed.

**Cards:**
1. **System Stats** — CPU, Memory, Disk (percentage bars with color thresholds: >80% red, >60% yellow, else green) + Uptime
2. **Tasks** — Checkbox list with priority tags (high/medium/low), add task dialog with priority selector, snackbar feedback
3. **Activity** — Date-stamped activity feed (static mock data)

**Interactions:**
- Refresh button randomizes stats
- Add task dialog with title input + priority buttons
- Task completion toggling
- Snackbar on task add and data refresh

### 4.6 VaultPanel — Ceetex Document Viewer

**File:** `panels/VaultPanel.tsx`

A split-pane document browser with search and tag filtering.

**Features:**
- Search input (filters by title + content)
- Tag filter bar (All + unique tags from documents)
- Document list sidebar with active highlight
- Document detail view: title, type badge, tag chips, content in `<pre>` block
- 5 mock documents: USX Grid Specification, C64 Memory Map, Teletext Standards, Font Encoding Guide, GridUI Architecture
- Empty states for no documents and no selection

### 4.7 GridEditorPanel — Layer Editor & Character Map

**File:** `panels/GridEditorPanel.tsx`

A two-tab editor for managing grid layers and exploring character maps.

**Tab 1 — Layers:**
- List of all layers with: visibility toggle, color indicator, name, z-index, opacity slider, delete button
- Add layer form: name input + color picker + Add/Cancel buttons
- Layer count shown in canvas overlay

**Tab 2 — Chars:**
- 128-character grid (ASCII 0-127)
- Cells colored by glyph availability (32-126 = has glyph)
- Hover tooltip showing character, Unicode codepoint, and decimal value
- Grid layout: compact cells with index number below character

**Canvas:**
- Fixed 640×384px SVG grid (80×24 cells at 8×16px each)
- Grid lines at 0.3 opacity
- Layer overlays with colored borders and name labels
- Center text showing current dimensions and visible layer count

### 4.8 SettingsPanel — Viewport & Display Configuration

**File:** `panels/SettingsPanel.tsx`

**Sections:**
1. **Viewport** — Columns (40-160) and Rows (12-60) number inputs
2. **Display Mode** — Teletext (full color), Monochrome (grayscale), Wireframe (high contrast)
3. **Font Size** — Preset buttons: 12, 14, 16, 18, 20, 24
4. **Color Palette** — Modern Dark, C64 Blue, Teletext, NES Classic (each with 4-color swatch)
5. **Options** — Show border toggle, Show chat sheet toggle

**Palette definitions:**
```typescript
PALETTES = [
  { id: 'modern',   name: 'Modern Dark',  colors: ['#0d1117', '#161b22', '#30363d', '#58a6ff'] },
  { id: 'c64',      name: 'C64 Blue',     colors: ['#352879', '#6c5ce7', '#a29bfe', '#dfe6e9'] },
  { id: 'teletext', name: 'Teletext',     colors: ['#000000', '#00ff00', '#ffff00', '#ffffff'] },
  { id: 'nes',      name: 'NES Classic',  colors: ['#181a1b', '#e08a3e', '#c84c0c', '#f8d8b8'] },
]
```

### 4.9 SurfaceToolbar — Viewport Dropdown & Nav Keypad

**File:** `panels/SurfaceToolbar.tsx`

**ViewportDropdown:**
- Floating button at bottom-right of main content
- Shows current dimensions (e.g., "80×24")
- Dropup menu with presets: 40×25, 80×24, 60×24, 40×24, 80×48, 120×36
- Active preset highlighted
- Click-outside-to-close behavior

**NavKeypad:**
- Arrow buttons for incrementing/decrementing cols and rows
- Home button to reset to 80×24
- Compact 3×3 grid layout

---

## 5. USX Integration

### 5.1 Token Mappings (surface-host.css)

GridUI maps all its visual properties to USX design tokens for consistency:

```css
:root {
  --grid-bg:              var(--usx-color-background, #0d1117);
  --grid-text:            var(--usx-color-on-background, #e6edf3);
  --grid-text-secondary:  var(--usx-color-on-surface-variant, #8b949e);
  --grid-bg-card:         var(--usx-color-surface-container, #161b22);
  --grid-bg-hover:        var(--usx-color-surface-container-high, #1c2333);
  --grid-border-light:    var(--usx-color-outline-variant, #21262d);
  --grid-border:          var(--usx-color-outline, #30363d);
  --gridui-surface-bg:    var(--usx-color-background, #0d1117);
  --gridui-viewport-text: var(--usx-color-on-background, #e6edf3);
  --gridui-viewport-bg:   var(--usx-color-surface, #0d1117);
  --gridui-border-bg:     var(--usx-color-surface-container, #161b22);
  --gridui-dynamic-zoom:  1;
  --gridui-viewport-padding: 0px;
}
```

### 5.2 Surface Layout Classes

GridUI uses the USX v3.1 surface layout pattern:
- `usx-surface-body` — flex container for nav rail + main content
- `usx-nav-rail` — vertical navigation rail (collapsible via `.collapsed` class)
- `usx-surface-main` — main content area

### 5.3 GlobalToolbar Integration

The `GlobalToolbar` component provides:
- Panel tabs (mapped from `PANELS` array)
- Chat toggle button
- Settings shortcut
- Sidebar toggle

---

## 6. Styling Architecture (gridui.css)

**File:** `uConnect/ui/src/styles/gridui.css` — 2268 lines

### 6.1 NestFrame Compliance

- `*:focus-visible` — 3px primary-colored outline (6px on large screens ≥1800×800)
- `@media (prefers-reduced-motion: reduce)` — disables all animations/transitions

### 6.2 Component Styles

| Section | Lines | Description |
|---------|-------|-------------|
| Chat Sheet | 438-574 | Fixed overlay chat panel |
| Snackbar | 576-626 | Bottom-center toast notifications |
| Panel Shared | 628-660 | `.gridui-panel`, `.gridui-panel-header`, `.gridui-panel-body` |
| Card | 662-681 | `.gridui-card`, `.gridui-card-header`, `.gridui-card-body` |
| Buttons | 683-742 | `.gridui-btn`, primary/small/icon/close variants |
| Input | 744-757 | `.gridui-input` with focus state |
| Tag/Badge | 759-772 | `.gridui-tag` with high/medium/low color variants |
| Dialog/Modal | 774-799 | Overlay + dialog box |
| Agent Switcher | 801-838 | Chat agent tab bar |
| Prompt Cards | 840-896 | Horizontal scrolling prompt row |
| Prose Output | 898-1000+ | Markdown rendering (headings, code, tables, blockquotes) |

### 6.3 Color System

All colors use CSS custom properties mapped to USX tokens. The palette system (modern/c64/teletext/nes) is implemented via the Settings panel but currently only affects the swatch display — actual token values remain USX-based.

---

## 7. Current State & Known Gaps

### 7.1 What Works
- ✅ All 6 panels render and are navigable via nav rail
- ✅ **grid-algebra** — GridCell, GridTransform, ColourPalette, TeletextPage modules
- ✅ **GridBufferRenderer** — shared renderer for all grid-based panels
- ✅ **GridWidget** — embeddable grid renderer for any surface
- ✅ **TeletextPanel** — Ceefax-style page viewer with 3-digit navigation
- ✅ **40×25 viewport preset** — teletext-native dimensions
- ✅ Viewport dimensions configurable (cols/rows) with presets
- ✅ Display modes: teletext, monochrome, wireframe
- ✅ Border modes: 1 (wide), 2 (medium), 3 (borderless)
- ✅ Font size presets (12-24px)
- ✅ Color palette selection (UI only — visual effect not fully wired)
- ✅ Grid layers: add, remove, toggle visibility, adjust opacity
- ✅ Character map: 128-char ASCII grid with hover tooltips
- ✅ C64 BASIC terminal with 15+ commands
- ✅ Dashboard with stats, tasks, activity
- ✅ Vault document browser with search + tag filter
- ✅ Chat sheet with simulated responses
- ✅ Snackbar notification system
- ✅ localStorage persistence for all preferences
- ✅ Nav rail collapse/expand
- ✅ Viewport dropdown with 5 presets
- ✅ Nav keypad for fine-grained viewport adjustment

### 7.2 Known Gaps
- ⚠️ **Palette visual effect partially wired** — GridBufferRenderer uses palette colours, but CSS tokens not fully dynamic
- ⚠️ **Terminal is simulated** — no real C64 emulator backend, just command parsing
- ⚠️ **Dashboard data is mock** — no real system stats integration
- ⚠️ **Vault documents are mock** — no real Ceetex/vault backend
- ⚠️ **Chat is simulated** — no real AI backend, just echo responses
- ⚠️ **Grid canvas is static** — no actual cell editing, just layer visualization
- ⚠️ **No real-time updates** — no WebSocket/SSE for live data
- ⚠️ **No keyboard shortcuts** — no key bindings for panel switching or commands

### 7.3 Integration Points
- **USX Design System** — Full token mapping via CSS variables
- **UIHubManager** — Registered as core surface, port 5178
- **GlobalToolbar** — Shared surface header component
- **Snackbar API** — Can trigger surface actions (start/stop/restart/repair/debug)

---

## 8. Quick Reference

| Aspect | Value |
|--------|-------|
| Surface ID | `gridui` |
| Port | 5178 |
| Route | `http://localhost:5178` |
| Icon | `widgets` |
| Color | `#f0883e` |
| Cell | `L100-AA10-0101-1` |
| Store Key | `gridui-prefs` (localStorage) |
| Char Width | 9px |
| Char Height | 16px |
| Default Viewport | 80×24 |
| Font | `PetMe128`, `C64 User Mono`, `Courier New` |
| Framework | React + TypeScript |
| State | React hooks + Context |
| Styles | CSS custom properties + USX tokens |
| Panels | 6 (terminal, teletext, dashboard, vault, grid, settings) |
