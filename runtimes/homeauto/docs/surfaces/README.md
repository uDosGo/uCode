---
title: "uCode3 Surfaces"
status: draft
last_updated: 2026-05-17T00:14:16+10:00
category: readme
tags: [ucode3]
description: "**Status:** Active — Surface integration layer for uCode3"
---
# uCode3 Surfaces

**Status:** Active — Surface integration layer for uCode3

## Overview

Surfaces are the presentation layer of uCode3 — wrapping external applications and frameworks as USX-compatible components with LENS/SKIN/Router architecture. Each surface provides a self-contained workspace that can be themed, routed, and state-managed through the uCode3 runtime.

## Registered Surfaces

| Surface | ID | Status | Description |
|---------|----|--------|-------------|
| **Jotion** | `jotion-document-workspace` | 🟡 Planning | Notion-style document workspace (Next.js 13, Convex, BlockNote) |
| HomeKit | `uhome-thin-kiosk` | 🟢 Active | Home media console (Tailwind + USXD) |
| Steam | `steam-console` | ⚪ Future | Steam launcher surface |

## Surface Architecture

```
surfaces/
├── jotion/                    # Jotion Notion clone surface
│   ├── lens/                  # LENS variable schemas
│   │   └── jotion-schema.json
│   ├── skin/                  # SKIN theme definitions
│   │   └── jotion-skin.json
│   ├── router/                # USX Router mappings
│   │   └── jotion-router.json
│   ├── components/            # React components
│   │   ├── JotionSurface.tsx
│   │   ├── DocumentEditor.tsx
│   │   ├── NavigationSidebar.tsx
│   │   ├── DocumentList.tsx
│   │   ├── CoverImage.tsx
│   │   └── DocumentIcon.tsx
│   ├── surface-definition.json  # Complete USX surface definition
│   ├── register.ts              # Surface registration
│   ├── next.config.js           # Next.js configuration
│   └── docker-compose.jotion.yml # Docker deployment
└── README.md                 # This file
```

## Surface Lifecycle

1. **Register** — Surface is registered with the uCode3 runtime via `registerSurface()`
2. **Mount** — LENS state is initialized with defaults from schema
3. **Render** — SKIN theme is applied, Router maps LENS → SKIN
4. **Interact** — User actions update LENS state, Router propagates changes
5. **Unmount** — Surface state is persisted, resources released

## Creating a New Surface

1. Create directory under `surfaces/<name>/`
2. Define LENS schema (`lens/<name>-schema.json`)
3. Define SKIN schema (`skin/<name>-skin.json`)
4. Define Router mappings (`router/<name>-router.json`)
5. Create surface definition (`surface-definition.json`)
6. Implement components (`components/`)
7. Register surface (`register.ts`)
8. Document in `docs/surfaces/`

## USX Protocol

Each surface communicates with the uCode3 runtime through the USX protocol:

- **LENS** → State variables (document, workspace, runtime)
- **SKIN** → Theme tokens (colors, typography, components)
- **Router** → Transform mappings (LENS → SKIN)
- **Surface** → Component tree (React components)

See `docs/surfaces/JOTION_SURFACE_INTEGRATION.md` for the complete integration guide.
