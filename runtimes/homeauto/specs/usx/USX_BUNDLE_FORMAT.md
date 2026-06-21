# USX Bundle Format Specification v1.0.0

**Status:** Active
**Updated:** 2026-05-17
**Schema URI:** `https://usx.dev/schema/bundle-v1`

---

## 1. Overview

The USX Bundle format (`.usx`) is a portable JSON file that combines three layers of a UI surface into a single, self-contained package:

| Layer | Schema | Purpose |
|-------|--------|---------|
| **LENS** | `lens.schema.json` | Dynamic state, variables, component states |
| **SKIN** | `skin.schema.json` | Visual styling, colors, typography, effects |
| **Layout** | `layout.schema.json` | Structural layout, widgets, grid, containers |

### 1.1 File Extension

- `.usx` — Standard USX bundle file
- `.usx.json` — Alternative extension for JSON-aware editors

### 1.2 MIME Type

`application/vnd.usx.bundle+json`

---

## 2. File Structure

```json
{
  "$schema": "https://usx.dev/schema/bundle-v1",
  "version": "1.0.0",
  "id": "my-surface-001",
  "name": "My Surface",
  "description": "A sample USX surface bundle",
  "source": {
    "tool": "figma",
    "version": "1.0.0",
    "exported_at": "2026-05-17T10:00:00Z",
    "exported_by": "user@example.com"
  },
  "lens": { ... },
  "skin": { ... },
  "layout": { ... },
  "meta": {
    "tags": ["ui", "dashboard"],
    "categories": ["surface"],
    "preview_image": "preview.png"
  }
}
```

---

## 3. LENS Section

The LENS section defines all dynamic state and variables. See `lens.schema.json` for full schema.

### 3.1 Variables

```json
{
  "lens": {
    "version": "1.0.0",
    "variables": {
      "userName": {
        "type": "string",
        "default": "Guest",
        "description": "Current user display name"
      },
      "isLoggedIn": {
        "type": "boolean",
        "default": false
      },
      "theme": {
        "type": "enum",
        "enum_values": ["light", "dark", "system"],
        "default": "system"
      },
      "itemCount": {
        "type": "number",
        "default": 0,
        "min": 0
      }
    },
    "components": {
      "submitButton": {
        "type": "button",
        "states": {
          "default": { "props": { "label": "Submit" } },
          "loading": { "props": { "label": "Submitting..." }, "style_overrides": { "opacity": "0.7" } },
          "disabled": { "props": { "label": "Submit" }, "style_overrides": { "cursor": "not-allowed" } }
        },
        "current_state": "default"
      }
    },
    "runtime": {
      "session_id": "sess_abc123",
      "connection_status": "connected",
      "last_sync": "2026-05-17T10:00:00Z",
      "unsaved_changes": false
    },
    "features": {
      "dark_mode": true,
      "animations": true,
      "offline_mode": false
    }
  }
}
```

### 3.2 Variable References

Widgets in the Layout section reference LENS variables using dot notation:

```
lens_ref: "variables.userName"
lens_ref: "components.submitButton.current_state"
lens_ref: "runtime.connection_status"
```

---

## 4. SKIN Section

The SKIN section defines all visual styling. See `skin.schema.json` for full schema.

### 4.1 Example

```json
{
  "skin": {
    "version": "1.0.0",
    "id": "wireframe-console-scaffold",
    "name": "Wireframe Console Scaffold",
    "inherits": "usx://themes/monochrome",
    "framework": "tailwind",
    "colors": {
      "background": { "light": "#ffffff", "dark": "#1a1a1a", "css_variable": "--usx-bg" },
      "surface": { "light": "#f8f9fa", "dark": "#2a2a2a", "css_variable": "--usx-surface" },
      "text": { "light": "#212529", "dark": "#e0e0e0", "css_variable": "--usx-text" },
      "text_muted": { "light": "#6c757d", "dark": "#808080", "css_variable": "--usx-text-muted" },
      "border": { "light": "#dee2e6", "dark": "#3a3a3a", "css_variable": "--usx-border" },
      "primary": { "light": "#0d6efd", "dark": "#00ff00", "css_variable": "--usx-primary" },
      "accent": { "light": "#6610f2", "dark": "#00ccff", "css_variable": "--usx-accent" },
      "error": { "light": "#dc3545", "dark": "#ff3333", "css_variable": "--usx-error" },
      "warning": { "light": "#ffc107", "dark": "#ffaa00", "css_variable": "--usx-warning" },
      "success": { "light": "#198754", "dark": "#00ff88", "css_variable": "--usx-success" }
    },
    "typography": {
      "body": { "font_family": "Inter, system-ui", "font_size": "16px", "font_weight": 400, "line_height": 1.5 },
      "h1": { "font_family": "Inter, system-ui", "font_size": "40px", "font_weight": 700, "line_height": 1.2 },
      "h2": { "font_family": "Inter, system-ui", "font_size": "28px", "font_weight": 600, "line_height": 1.3 },
      "code": { "font_family": "SF Mono, monospace", "font_size": "14px", "font_weight": 400, "line_height": 1.5 },
      "caption": { "font_family": "Inter, system-ui", "font_size": "14px", "font_weight": 400, "line_height": 1.4 }
    },
    "spacing": {
      "xs": { "value": "4px" },
      "sm": { "value": "8px" },
      "md": { "value": "16px" },
      "lg": { "value": "24px" },
      "xl": { "value": "32px" }
    },
    "effects": {
      "shadow_sm": { "type": "shadow", "value": "0 1px 2px rgba(0,0,0,0.05)" },
      "shadow_md": { "type": "shadow", "value": "0 4px 6px rgba(0,0,0,0.1)" },
      "scanline": { "type": "scanline", "value": "repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.03) 2px, rgba(0,0,0,0.03) 4px)" }
    },
    "components": {
      "button": {
        "base": "inline-flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all",
        "variants": {
          "primary": "bg-primary text-white hover:brightness-110",
          "secondary": "bg-surface border border-border text-text hover:bg-border",
          "danger": "bg-error text-white hover:brightness-110"
        },
        "states": {
          "disabled": "opacity-50 cursor-not-allowed",
          "loading": "animate-pulse"
        }
      },
      "card": {
        "base": "bg-surface border border-border rounded-lg p-4",
        "variants": {
          "elevated": "shadow-md",
          "flat": "shadow-none"
        }
      }
    }
  }
}
```

---

## 5. Layout Section

The Layout section defines the structural layout. See `layout.schema.json` for full schema.

### 5.1 Example

```json
{
  "layout": {
    "version": "1.0.0",
    "type": "surface",
    "title": "Dashboard",
    "viewport": {
      "width": "100%",
      "max_width": "1200px"
    },
    "grid": {
      "template_columns": "repeat(3, 1fr)",
      "gap": "16px"
    },
    "root": {
      "id": "root",
      "type": "container",
      "children": [
        {
          "id": "header",
          "type": "container",
          "skin_ref": "components.card",
          "children": [
            {
              "id": "title",
              "type": "heading",
              "content": { "text": "Welcome, {{variables.userName}}" },
              "skin_ref": "typography.h1"
            },
            {
              "id": "submit-btn",
              "type": "button",
              "lens_ref": "components.submitButton",
              "events": {
                "onClick": { "action": "submit_form", "payload": {} }
              }
            }
          ]
        },
        {
          "id": "stats-grid",
          "type": "container",
          "repeat": {
            "source": "data.stats",
            "as": "stat"
          },
          "children": [
            {
              "id": "stat-card",
              "type": "card",
              "content": { "title": "{{stat.name}}", "value": "{{stat.value}}" }
            }
          ]
        }
      ]
    }
  }
}
```

### 5.2 Template Syntax

Layout content can reference LENS variables using `{{variable.path}}` syntax:

| Syntax | Resolution |
|--------|-----------|
| `{{variables.userName}}` | Resolves to `lens.variables.userName` value |
| `{{runtime.connection_status}}` | Resolves to `lens.runtime.connection_status` value |
| `{{stat.name}}` | Resolves to current item in a `repeat` loop |

---

## 6. Bundle File Naming Convention

```
{source}-{name}-{version}.usx

Examples:
  figma-dashboard-v1.usx
  xd-login-flow-v2.usx
  monodraw-layout-v1.usx
  ucode3-document-v1.usx
```

---

## 7. Bundle Distribution

### 7.1 Local File System

```
~/.local/share/udos/surfaces/
├── my-surface/
│   ├── bundle.usx
│   ├── assets/
│   │   ├── logo.png
│   │   └── background.jpg
│   └── preview.png
```

### 7.2 WebSocket Stream

Bundles can be streamed over WebSocket for live editing:

```json
{
  "type": "usx_bundle_update",
  "bundle_id": "my-surface-001",
  "patch": {
    "lens.variables.userName": "Alice",
    "skin.colors.primary.light": "#ff0000"
  }
}
```

---

## 8. Validation

Bundles should be validated against the JSON schemas:

```bash
# Using ajv CLI
ajv validate -s bundle.schema.json -d my-surface.usx

# Using Node.js
const Ajv = require('ajv');
const ajv = new Ajv();
const validate = ajv.compile(require('./bundle.schema.json'));
const valid = validate(bundle);
```

---

## 9. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-05-17 | Initial specification |

---

## 10. References

- `lens.schema.json` — LENS schema definition
- `skin.schema.json` — SKIN schema definition
- `layout.schema.json` — Layout schema definition
- `bundle.schema.json` — Bundle schema definition
- `converter-core/` — Converter module for design tool → USX
