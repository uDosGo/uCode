---
title: "uCode4 Themes"
status: draft
last_updated: 2026-05-17T00:14:16+10:00
category: readme
tags: [ucode4]
description: "**Status:** Active — Theme layer for uCode4 console scaffold"
---
# uCode4 Themes

**Status:** Active — Theme layer for uCode4 console scaffold

## Overview

Themes define the visual presentation layer for uCode4 surfaces. Each theme provides a complete set of color tokens, typography, component classes, and effects that can be applied to any surface through the USX SKIN protocol.

## Registered Themes

| Theme | ID | Status | Description |
|-------|----|--------|-------------|
| **Wireframe** | `wireframe-console-scaffold` | 🟢 Active | Monochrome console scaffold (default) |
| Matrix | `matrix-green` | ⚪ Future | Green-on-black terminal theme |
| Light | `wireframe-light` | ⚪ Future | Light mode variant |
| Retro | `retro-terminal` | ⚪ Future | Amber/green phosphor theme |

## Theme Architecture

```
themes/
├── wireframe/                 # Wireframe console scaffold
│   ├── wireframe-skin.json    # SKIN schema
│   ├── wireframe.css          # Component styles
│   └── wireframe-vars.css     # CSS custom properties
├── README.md                  # This file
└── WIREFRAME_THEME.md         # Wireframe theme documentation
```

## Theme Lifecycle

1. **Register** — Theme is registered with the uCode4 runtime
2. **Load** — CSS variables are injected into the document root
3. **Apply** — Component classes are mapped to theme tokens
4. **Switch** — Theme can be hot-swapped at runtime
5. **Unload** — Theme resources are released

## Creating a New Theme

1. Create directory under `themes/<name>/`
2. Define SKIN schema (`<name>-skin.json`)
3. Create CSS with custom properties (`<name>.css`)
4. Document theme tokens (`docs/themes/<NAME>_THEME.md`)
5. Register theme in the runtime

## USX SKIN Protocol

Each theme communicates through the USX SKIN protocol:

- **Color tokens** → CSS custom properties (`--wf-*`)
- **Typography** → Font families and sizes
- **Components** → CSS class names
- **Effects** → Animation and transition classes

See `docs/themes/WIREFRAME_THEME.md` for the complete wireframe theme documentation.
