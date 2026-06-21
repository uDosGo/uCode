# USX Phase 2 — Registry, Figma Plugin, Validation & Dark Mode

**Date:** 2026-05-17
**Status:** ✅ Complete
**Next:** Phase 3 — uDosGo Integration & Animation System

---

## What Was Built

Phase 2 delivers four major additions to the USX ecosystem:

1. **Bundle Registry** — SQLite-backed local storage with full-text search
2. **Figma Plugin** — Direct export from Figma to USX bundles
3. **Schema Validation** — Ajv-based validation against JSON schemas
4. **Dark Mode** — Automatic and manual dark mode switching in the renderer

---

## 1. Bundle Registry (`registry/`)

A local SQLite database for storing, indexing, searching, and managing USX bundles.

### Features

| Feature | Description |
|---------|-------------|
| **SQLite Storage** | Persistent bundle storage with WAL mode |
| **Full-Text Search** | FTS5-based search across name, description, and tags |
| **Tag/Category Filtering** | Filter bundles by tags and categories |
| **Version History** | Track all imported versions of each bundle |
| **Directory Import** | Bulk import all `.usx` files from a directory |
| **Registry Stats** | Total bundles, tags, sources, recent imports |

### Database Schema

- `bundles` — Core bundle metadata + raw JSON
- `tags` — Tag associations (many-to-many)
- `categories` — Category associations
- `dependencies` — Bundle dependency tracking
- `versions` — Version history
- `bundles_fts` — FTS5 virtual table for full-text search

### CLI Usage

```bash
# Initialize registry
node src/cli.js init ./usx-registry.db

# Import bundles
node src/cli.js import ../examples ./usx-registry.db

# Search
node src/cli.js search dashboard

# List all bundles
node src/cli.js list

# Get bundle details
node src/cli.js get dashboard-001

# Show stats
node src/cli.js stats

# List all tags
node src/cli.js tags

# Show version history
node src/cli.js versions dashboard-001

# Delete a bundle
node src/cli.js delete dashboard-001
```

---

## 2. Figma Plugin (`figma-plugin/`)

A Figma plugin that exports frames, components, and pages to the USX Bundle Format.

### Features

| Feature | Description |
|---------|-------------|
| **Export Selection** | Export selected frame(s) as individual USX bundles |
| **Export Page** | Export entire page as a multi-widget layout |
| **Node Conversion** | Maps Figma node types → USX widget types |
| **SKIN Extraction** | Extracts colors, typography, and effects to SKIN |
| **LENS Extraction** | Extracts text content as LENS variables |
| **Auto Layout** | Converts Figma auto-layout to flexbox props |
| **Copy/Download** | Copy bundle JSON or download `.usx` file |

### Files

| File | Purpose |
|------|---------|
| `manifest.json` | Figma plugin manifest |
| `code.js` | Plugin sandbox code (node conversion, SKIN/LENS extraction) |
| `ui.html` | Plugin UI (export buttons, options, copy/download) |

### Node Type Mapping

| Figma Type | USX Widget |
|------------|------------|
| FRAME, GROUP | `container` |
| TEXT | `text` |
| RECTANGLE, ELLIPSE, POLYGON, STAR | `container` |
| LINE | `divider` |
| VECTOR, BOOLEAN_OPERATION | `icon` |
| INSTANCE, COMPONENT | `container` |
| SECTION | `card` |

---

## 3. Schema Validation (`converter-core/src/validate-schema.js`)

Full Ajv-based validation of USX bundles against their JSON schemas.

### Features

| Feature | Description |
|---------|-------------|
| **Bundle Validation** | Validates complete bundles against `bundle.schema.json` |
| **Section Validation** | Validates individual LENS, SKIN, Layout sections |
| **Cross-Section Validation** | Checks template references exist in LENS |
| **Custom Formats** | `usx-template`, `css-variable`, `hex-color`, `semver` |
| **File Validation** | Validate `.usx` files from disk |
| **Formatted Output** | Human-readable validation results |

### Validation Checks

- **Required fields**: `version`, `id`, `name`, `lens`, `skin`, `layout`
- **LENS**: Variable name format, type validation, connection status
- **SKIN**: Framework, color hex format, typography completeness, component structure
- **Layout**: Widget type validation, required `id`/`type`, children structure, repeat config
- **Cross-section**: Template `{{variables.xxx}}` references exist in LENS

### API Endpoint

The preview server now includes a validation endpoint:

```
GET /api/validate?bundle=dashboard-001
```

---

## 4. Dark Mode Support

The renderer now supports both automatic (system preference) and manual dark mode switching.

### Features

| Feature | Description |
|---------|-------------|
| **CSS Variables** | `:root` and `@media (prefers-color-scheme: dark)` |
| **SKIN Dark Values** | Uses `color.dark` when available, falls back to `color.light` |
| **Manual Toggle** | Floating button toggles `.usx-dark-mode` class |
| **Runtime API** | `usx.toggleDarkMode()`, `usx.isDarkMode()` |
| **Query Param** | `?_darkMode=true` to force dark mode |
| **Custom Events** | `usx:darkmode` event dispatched on toggle |

### How It Works

1. **Light mode**: `:root { --usx-bg: #f8fafc; ... }`
2. **Dark mode**: `@media (prefers-color-scheme: dark) { :root { --usx-bg: #0f172a; ... } }`
3. **Manual toggle**: `:root.usx-dark-mode { --usx-bg: #0f172a; ... }`
4. **SKIN colors**: Each color can have `light` and `dark` values
5. **Bundle feature**: `lens.features.dark_mode: true` enables dark mode by default

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
├── PHASE2_SUMMARY.md
├── converter-core/
│   ├── package.json
│   └── src/
│       ├── index.js
│       ├── validate.js
│       ├── validate-schema.js       ← NEW: Ajv-based schema validation
│       ├── watcher.js
│       └── converters/
│           └── figma-to-usx.js
├── renderer/
│   ├── package.json
│   └── src/
│       ├── renderer.js              ← UPDATED: Dark mode support
│       ├── server.js                ← UPDATED: Validate API, dark mode query param
│       └── cli.js
├── registry/                        ← NEW: Bundle registry
│   ├── package.json
│   └── src/
│       ├── index.js                 ← Registry class (SQLite, FTS, search)
│       └── cli.js                   ← Registry CLI
├── figma-plugin/                    ← NEW: Figma export plugin
│   ├── manifest.json
│   ├── code.js
│   └── ui.html
└── examples/
    ├── hello-world.usx
    └── dashboard.usx
```

---

## Phase 3 Roadmap

- [ ] **uDosGo Integration** — Surface loading in uDosGo engine
- [ ] **Animation System** — Widget enter/exit animations
- [ ] **Bundle Dependencies** — Import/export between bundles
- [ ] **Component Library** — Reusable USX component catalog
- [ ] **Live Editing** — In-browser bundle editor with preview
- [ ] **Export to HTML/CSS** — Standalone static site generation
