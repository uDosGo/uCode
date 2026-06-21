# USX Phase 3 — uDosGo Integration, Animation System & Bundle Dependencies

**Date:** 2026-05-17
**Status:** ✅ Complete
**Next:** Phase 4 — Component Library & Live Editing

---

## What Was Built

Phase 3 delivers three major additions to the USX ecosystem:

1. **uDosGo Integration** — Surface loader for embedding USX in the uDosGo engine
2. **Animation System** — 12 CSS keyframe animations with staggered support
3. **Bundle Dependencies** — Import/export and merging between bundles

---

## 1. uDosGo Integration (`udos-loader/`)

A surface loader that loads and manages USX surfaces within the uDosGo engine.

### Features

| Feature | Description |
|---------|-------------|
| **Surface Lifecycle** | Load, show, hide, reload, destroy surfaces |
| **Renderer Auto-Start** | Spawns USX renderer server if not running |
| **Iframe Embedding** | Renders surfaces in sandboxed iframes |
| **Event Bridging** | Bidirectional communication via `postMessage` |
| **WebSocket Live Updates** | Auto-reload on bundle file changes |
| **LENS Variable Control** | Set/get variables on running surfaces |
| **Event System** | `surface:show`, `surface:hide`, `surface:reload`, `widget:event`, `variable:update`, `darkmode:toggle` |

### Usage

```js
import { SurfaceLoader } from './src/index.js';

const loader = new SurfaceLoader({ baseDir: './bundles' });
await loader.init();

const surface = loader.loadSurface('./dashboard.usx');
surface.show('#app-container');

surface.on('widget:event', (detail) => {
  console.log('Widget event:', detail);
});

surface.setVariable('variables.theme', 'dark');
```

---

## 2. Animation System

The renderer now includes 12 CSS keyframe animations that can be applied to any widget.

### Available Animations

| Animation | Keyframe | Default Duration |
|-----------|----------|-----------------|
| `fade-in` | Opacity 0 → 1 | 300ms |
| `fade-out` | Opacity 1 → 0 | 300ms |
| `slide-in-up` | TranslateY(20px) → 0 | 300ms |
| `slide-in-down` | TranslateY(-20px) → 0 | 300ms |
| `slide-in-left` | TranslateX(-20px) → 0 | 300ms |
| `slide-in-right` | TranslateX(20px) → 0 | 300ms |
| `scale-in` | Scale(0.9) → 1 | 300ms |
| `rotate-in` | Rotate(-10deg) → 0 | 300ms |
| `bounce-in` | Scale(0) → 1.15 → 0.95 → 1 | 500ms |
| `pulse` | Opacity 1 → 0.5 → 1 (infinite) | 2s |
| `shake` | TranslateX(0 → -5 → 5 → 0) | 500ms |
| `spin` | Rotate(0 → 360deg, infinite) | 1s |

### Staggered Animation

The `.usx-stagger` class applies staggered fade-in to child widgets with 50ms delays:

```json
{
  "id": "list",
  "type": "container",
  "animation": { "enter": "fade-in", "stagger": true },
  "children": [
    { "id": "item-1", "type": "text", "content": { "text": "Item 1" } },
    { "id": "item-2", "type": "text", "content": { "text": "Item 2" } }
  ]
}
```

### Widget Animation Props

```json
{
  "id": "hero",
  "type": "container",
  "animation": {
    "enter": "slide-in-up",
    "duration": 500,
    "delay": 100,
    "stagger": false
  }
}
```

Or as a shorthand string:
```json
{
  "id": "hero",
  "type": "container",
  "animation": "fade-in"
}
```

---

## 3. Bundle Dependencies (`converter-core/src/dependencies.js`)

A dependency resolver that manages imports between USX bundles.

### Features

| Feature | Description |
|---------|-------------|
| **Dependency Resolution** | Topological sort of dependency trees |
| **Circular Detection** | Detects and reports circular dependencies |
| **Bundle Merging** | Merge dependent bundles into a single composite |
| **Version Checking** | Major/minor version compatibility |
| **Widget ID Prefixing** | Prevents ID conflicts during merge |
| **Deep Merge** | Recursive merge of LENS and SKIN sections |
| **Validation** | Validate all dependencies for a bundle |

### Bundle Format

Bundles declare dependencies in their root:

```json
{
  "id": "dashboard",
  "name": "Dashboard",
  "version": "1.0.0",
  "dependencies": {
    "chart-widget": "^1.0.0",
    "data-table": "^2.0.0"
  },
  "imports": ["header-bar"],
  "lens": { ... },
  "skin": { ... },
  "layout": { ... }
}
```

### Usage

```js
import { DependencyResolver } from './dependencies.js';

const resolver = new DependencyResolver();
resolver.loadBundle('./chart-widget.usx');
resolver.loadBundle('./dashboard.usx');

// Resolve dependency order
const order = resolver.resolveDependencies('dashboard');
// → ['chart-widget', 'dashboard']

// Merge into single bundle
const merged = resolver.mergeBundles('dashboard');

// Validate
const result = resolver.validateDependencies('dashboard');

// Get dependency tree
const tree = resolver.getDependencyTree('dashboard');
```

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
├── PHASE3_SUMMARY.md                    ← NEW
├── converter-core/
│   ├── package.json
│   └── src/
│       ├── index.js
│       ├── validate.js
│       ├── validate-schema.js
│       ├── dependencies.js              ← NEW: Bundle dependency resolver
│       ├── watcher.js
│       └── converters/
│           └── figma-to-usx.js
├── renderer/
│   ├── package.json
│   └── src/
│       ├── renderer.js                  ← UPDATED: Animation keyframes + widget animation props
│       ├── server.js
│       └── cli.js
├── registry/
│   ├── package.json
│   └── src/
│       ├── index.js
│       └── cli.js
├── udos-loader/                         ← NEW: uDosGo surface loader
│   ├── package.json
│   └── src/
│       └── index.js
├── figma-plugin/
│   ├── manifest.json
│   ├── code.js
│   └── ui.html
└── examples/
    ├── hello-world.usx
    └── dashboard.usx
```

---

## Phase 4 Roadmap

- [ ] **Component Library** — Reusable USX component catalog with preview
- [ ] **Live Editing** — In-browser bundle editor with real-time preview
- [ ] **Export to HTML/CSS** — Standalone static site generation
- [ ] **Performance Profiling** — Bundle size analysis and render timing
- [ ] **Internationalization** — Multi-language LENS variable support
- [ ] **Accessibility** — ARIA attributes, keyboard navigation, screen reader support
