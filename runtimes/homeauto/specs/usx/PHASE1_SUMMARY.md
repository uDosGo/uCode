# USX Phase 1 — Renderer & Live Preview Complete

**Date:** 2026-05-17
**Status:** ✅ Complete
**Next:** Phase 2 — Bundle Registry & Figma Plugin

---

## What Was Built

Phase 1 delivers the **USX Renderer Engine** — a full HTML/CSS renderer that converts USX bundles into browser-ready pages, plus a **Live Preview Server** with WebSocket-based hot reload.

### Renderer (`renderer/`)

| File | Purpose |
|------|---------|
| `src/renderer.js` | Core renderer: converts USX bundles → HTML + CSS + JS |
| `src/server.js` | HTTP + WebSocket preview server with live reload |
| `src/cli.js` | CLI tool: render, serve, watch, validate, info |

### Examples (`examples/`)

| File | Purpose |
|------|---------|
| `hello-world.usx` | Simple demo with LENS variables, conditions, and SKIN theming |
| `dashboard.usx` | Full analytics dashboard with grid layout, cards, tables, and data binding |

---

## Renderer Capabilities

### LENS Resolution
- **Template variables**: `{{variables.userName}}` → resolved at render time
- **Conditional rendering**: `condition: "!variables.isLoggedIn"` → show/hide widgets
- **Runtime overrides**: Query params like `?lens.variables.userName=Alice` override LENS at serve time
- **Repeat loops**: `repeat: { source: "data.stats", as: "stat" }` → iterate over arrays

### SKIN → CSS Generation
- **CSS variables**: `--usx-primary`, `--usx-bg`, etc. from SKIN colors
- **Typography classes**: `.usx-h1`, `.usx-body`, `.usx-caption` from SKIN typography
- **Component classes**: `.usx-button`, `.usx-card`, `.usx-badge` from SKIN components
- **Variant classes**: `.usx-button.usx-primary`, `.usx-card.usx-elevated`
- **State classes**: `.usx-button.usx-state-disabled`
- **Effect classes**: `.usx-effect-shadow-md` from SKIN effects

### Widget → HTML Mapping
All 23 widget types are supported:
- Structural: `container`, `card`, `list`, `table`
- Content: `text`, `heading`, `image`, `icon`, `code_block`, `quote`, `callout`
- Interactive: `button`, `input`, `form`, `toggle`, `todo`
- Rich: `iframe`, `custom`

### Runtime JavaScript
- `window.usx` object with `handleEvent()`, `setVariable()`, `getVariable()`
- Custom events: `usx:event`, `usx:update`
- Debug mode: `#debug` hash for console logging

---

## Live Preview Server

### Features
- **HTTP server** on port 3333 (configurable)
- **WebSocket** for live reload on bundle changes
- **Bundle cache** with API endpoints:
  - `GET /api/bundles` — List loaded bundles
  - `GET /api/bundle/:id` — Get bundle JSON
  - `GET /api/reload` — Reload bundles from disk
- **File watching** (`--watch` flag) — auto-reload on `.usx` file changes
- **Bundle selector** — Index page when multiple bundles are loaded
- **Static file serving** — Assets from bundle directory

### Usage

```bash
# Start server with examples
node src/server.js ../examples 3333 --watch

# Or via CLI
node src/cli.js serve ../examples 3333
node src/cli.js watch ../examples 3333
```

---

## CLI Tool

```bash
# Render a bundle to HTML
node src/cli.js render ../examples/hello-world.usx output.html

# Start preview server
node src/cli.js serve ../examples 3333

# Start with file watching
node src/cli.js watch ../examples 3333

# Validate a bundle
node src/cli.js validate ../examples/hello-world.usx

# Show bundle info
node src/cli.js info ../examples/hello-world.usx
```

---

## Example: Hello World Bundle

The `hello-world.usx` bundle demonstrates:
- **LENS variables**: `userName`, `count`, `isLoggedIn`
- **Conditional rendering**: Login/logout sections based on `isLoggedIn`
- **SKIN theming**: Custom colors, typography, button/card components
- **Template resolution**: `{{variables.userName}}`, `{{variables.count}}`

### Preview with overrides:
```
http://localhost:3333/?lens.variables.userName=Alice&lens.variables.isLoggedIn=true
```

---

## Example: Analytics Dashboard

The `dashboard.usx` bundle demonstrates:
- **Grid layout**: 4-column stat cards, 2-column content area
- **Data binding**: `repeat` loop over `data.stats` array
- **Tables**: Recent orders with headers and rows
- **Multiple card variants**: `elevated`, `stat`, `flat`
- **Typography scale**: `h1`, `h2`, `stat_value`, `stat_label`, `caption`
- **Event handlers**: Buttons with `onClick` actions

---

## File Tree

```
specs/usx/
├── lens.schema.json
├── skin.schema.json
├── layout.schema.json
├── bundle.schema.json
├── USX_BUNDLE_FORMAT.md
├── PHASE0_SUMMARY.md
├── PHASE1_SUMMARY.md
├── converter-core/
│   ├── package.json
│   └── src/
│       ├── index.js
│       ├── validate.js
│       ├── watcher.js
│       └── converters/
│           └── figma-to-usx.js
├── renderer/
│   ├── package.json
│   └── src/
│       ├── renderer.js
│       ├── server.js
│       └── cli.js
└── examples/
    ├── hello-world.usx
    └── dashboard.usx
```

---

## Phase 2 Roadmap

- [ ] **Bundle Registry** — Local bundle storage, indexing, and search
- [ ] **Figma Plugin** — Direct export from Figma to USX via plugin
- [ ] **Schema Validation** — Full ajv-based validation against JSON schemas
- [ ] **Dark Mode** — Automatic dark mode switching via SKIN dark values
- [ ] **Animation System** — Widget enter/exit animations
- [ ] **uDosGo Integration** — Surface loading in uDosGo engine
