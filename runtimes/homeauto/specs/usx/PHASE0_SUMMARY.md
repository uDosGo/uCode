# USX Phase 0 — Foundation Complete

**Date:** 2026-05-17
**Status:** ✅ Complete
**Next:** Phase 1 — Renderer & Live Preview

---

## What Was Built

Phase 0 establishes the **USX Bundle Format** — a portable, three-layer JSON specification for describing UI surfaces that can be exported from design tools and rendered by the uDosGo engine.

### The Three Layers

```
┌─────────────────────────────────┐
│         USX Bundle (.usx)       │
├─────────────────────────────────┤
│  LENS  — Dynamic state/vars     │
│  SKIN  — Visual styling/theme   │
│  Layout — Structure/widgets     │
└─────────────────────────────────┘
```

### Files Created

| File | Purpose |
|------|---------|
| `lens.schema.json` | JSON Schema for dynamic state and variables |
| `skin.schema.json` | JSON Schema for visual styling and theme |
| `layout.schema.json` | JSON Schema for structural layout and widgets |
| `bundle.schema.json` | JSON Schema for the complete USX bundle |
| `USX_BUNDLE_FORMAT.md` | Full specification document with examples |
| `converter-core/` | Node.js module for bundle creation/validation/conversion |

### converter-core Module

| File | Purpose |
|------|---------|
| `src/index.js` | Core API: createBundle, loadBundle, saveBundle, mergeBundles, resolveTemplate, widget helpers |
| `src/validate.js` | Bundle validator (CLI + API) |
| `src/converters/figma-to-usx.js` | Figma JSON → USX converter |
| `src/watcher.js` | File watcher for auto-conversion |

---

## Key Design Decisions

### 1. Three-Layer Separation

- **LENS** = What (data/state) — changes at runtime
- **SKIN** = How (style/theme) — changes per context/user
- **Layout** = Where (structure) — changes per device/surface

This separation allows each layer to be independently versioned, swapped, or updated without affecting the others.

### 2. Template Syntax

Layout content uses `{{variable.path}}` syntax to reference LENS variables:

```json
{ "text": "Welcome, {{variables.userName}}" }
```

This enables dynamic content without embedding logic in the layout.

### 3. Widget System

Layouts are composed of widgets — typed UI elements with bounds, content, children, events, and conditional rendering. Widget types include:

- Structural: `container`, `card`, `list`, `table`
- Content: `text`, `heading`, `image`, `icon`, `code_block`, `quote`, `callout`
- Interactive: `button`, `input`, `form`, `toggle`, `todo`
- Rich: `mermaid`, `chart`, `map`, `video`, `audio`, `iframe`

### 4. Design Tool Agnostic

The `source` field in the bundle tracks which tool exported it:

```json
"source": { "tool": "figma", "version": "1.0.0" }
```

Converters can be written for any tool (Figma, Adobe XD, Sketch, MonoDraw, etc.) and all produce the same USX format.

---

## Usage Examples

### Creating a Bundle Programmatically

```js
import { createBundle, createText, createButton, saveBundle } from './converter-core/src/index.js';

const bundle = createBundle({
  id: 'hello-world',
  name: 'Hello World',
  lens: {
    variables: {
      name: { type: 'string', default: 'World' }
    }
  },
  skin: {
    id: 'default',
    name: 'Default',
    colors: { primary: { light: '#0d6efd' } }
  },
  layout: {
    root: createContainer('root', [
      createText('greeting', 'Hello, {{variables.name}}'),
      createButton('btn', 'Click Me')
    ])
  }
});

saveBundle('./hello-world.usx', bundle);
```

### Validating a Bundle

```bash
node src/validate.js my-surface.usx
```

### Converting Figma Export

```bash
node src/converters/figma-to-usx.js figma-export.json
# → Creates figma-export.usx
```

### Watching a Directory

```bash
node src/watcher.js ./exports ./bundles
```

---

## Phase 1 Roadmap

- [ ] **Renderer** — HTML/CSS renderer for USX bundles
- [ ] **Live Preview** — WebSocket-based live preview server
- [ ] **Figma Plugin** — Direct export from Figma to USX
- [ ] **Bundle Registry** — Local bundle storage and indexing
- [ ] **Schema Validation** — Full ajv-based validation against JSON schemas
- [ ] **uDosGo Integration** — Surface loading in uDosGo engine

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
└── converter-core/
    ├── package.json
    └── src/
        ├── index.js
        ├── validate.js
        ├── watcher.js
        └── converters/
            └── figma-to-usx.js
```
