---
title: "Wireframe Theme — uCode4 Console Scaffold"
status: draft
last_updated: 2026-05-17T00:14:16+10:00
category: documentation
tags: [ucode4]
description: "**Status:** Active — Console scaffold theme for uCode4"
---
# Wireframe Theme — uCode4 Console Scaffold

**Status:** Active — Console scaffold theme for uCode4
**Theme ID:** `wireframe-console-scaffold`
**Skin ID:** `wireframe-skin`
**Version:** 1.0.0
**Layer:** L300-L399 (Surface Layer)

---

## Overview

The Wireframe theme provides a minimal, monochrome console scaffold for uCode4. It serves as the base visual layer for all uCode4 surfaces — a clean, low-fidelity wireframe that prioritizes structure over decoration.

```
┌─────────────────────────────────────────────────────────────┐
│                    uCode4 Wireframe Console                   │
│                                                             │
│  ┌─────────┐  ┌──────────────────────────────────────────┐  │
│  │ LENS    │  │              SKIN Wireframe              │  │
│  │ State   │──│  ┌────────────────────────────────────┐  │  │
│  │         │  │  │  Monochrome Palette                │  │  │
│  │ snack   │  │  │  - Background: #1a1a1a             │  │  │
│  │ box     │  │  │  - Surface:   #2a2a2a              │  │  │
│  │         │  │  │  - Text:      #e0e0e0              │  │  │
│  │ runtime │  │  │  - Border:    #3a3a3a              │  │  │
│  │         │  │  │  - Accent:    #00ff00 (matrix)     │  │  │
│  └─────────┘  │  └────────────────────────────────────┘  │  │
│               │                                           │  │
│               │  ┌────────────────────────────────────┐  │  │
│               │  │  Component Classes                 │  │  │
│               │  │  - .console-frame                  │  │  │
│               │  │  - .surface-panel                  │  │  │
│               │  │  - .wireframe-header               │  │  │
│               │  │  - .wireframe-footer               │  │  │
│               │  └────────────────────────────────────┘  │  │
│               └──────────────────────────────────────────┘  │
│                                                             │
│  Output: Monochrome Console UI    │  Runtime: uCode4 Engine  │
└─────────────────────────────────────────────────────────────┘
```

---

## SKIN Schema

```json
{
  "$schema": "https://usx.dev/schema/skin-v1",
  "version": "1.0.0",
  "skin": {
    "id": "wireframe-console-scaffold",
    "name": "Wireframe Console Scaffold",
    "inherits": "usx://themes/monochrome",
    "framework": "Tailwind CSS",
    "overrides": {
      "color": {
        "background": "#1a1a1a",
        "surface": "#2a2a2a",
        "text": "#e0e0e0",
        "text_muted": "#808080",
        "border": "#3a3a3a",
        "primary": "#00ff00",
        "accent": "#00ccff",
        "error": "#ff3333",
        "warning": "#ffaa00",
        "success": "#00ff88"
      },
      "typography": {
        "body_font": "'Courier New', 'SF Mono', Monaco, monospace",
        "heading_font": "'Courier New', 'SF Mono', monospace",
        "mono_font": "'Courier New', 'SF Mono', monospace",
        "base_size": "14px",
        "line_height": "1.4"
      },
      "components": {
        "console_frame": "console-frame",
        "surface_panel": "surface-panel",
        "header": "wireframe-header",
        "footer": "wireframe-footer",
        "sidebar": "wireframe-sidebar",
        "content": "wireframe-content",
        "status_bar": "wireframe-status",
        "command_line": "wireframe-command"
      },
      "effects": {
        "hover": "brightness-110 transition",
        "focus": "ring-1 ring-primary",
        "active": "brightness-90",
        "selection": "bg-primary/20",
        "scanline": "scanline-effect"
      }
    },
    "extended": {
      "wireframe": {
        "border_style": "solid",
        "border_width": "1px",
        "corner_radius": "0px",
        "shadow": "none",
        "animation_speed": "0.15s",
        "scanlines": true,
        "crt_effect": false,
        "grid_overlay": false
      }
    }
  }
}
```

---

## Color Tokens

| Token | Hex | CSS Variable | Usage |
|-------|-----|-------------|-------|
| `background` | `#1a1a1a` | `--wf-bg` | Main background |
| `surface` | `#2a2a2a` | `--wf-surface` | Panel backgrounds |
| `text` | `#e0e0e0` | `--wf-text` | Primary text |
| `text_muted` | `#808080` | `--wf-text-muted` | Secondary text |
| `border` | `#3a3a3a` | `--wf-border` | Borders and dividers |
| `primary` | `#00ff00` | `--wf-primary` | Accent/matrix green |
| `accent` | `#00ccff` | `--wf-accent` | Cyan accent |
| `error` | `#ff3333` | `--wf-error` | Error states |
| `warning` | `#ffaa00` | `--wf-warning` | Warning states |
| `success` | `#00ff88` | `--wf-success` | Success states |

---

## Typography

| Level | Font | Size | Weight | Line Height | Usage |
|-------|------|------|--------|-------------|-------|
| Body | Courier New | 14px | 400 | 1.4 | Default text |
| Heading 1 | Courier New | 24px | 700 | 1.2 | Page titles |
| Heading 2 | Courier New | 20px | 600 | 1.3 | Section titles |
| Heading 3 | Courier New | 16px | 600 | 1.3 | Sub-section titles |
| Code | Courier New | 13px | 400 | 1.4 | Code blocks |
| Caption | Courier New | 12px | 400 | 1.3 | Labels, timestamps |
| Status | Courier New | 11px | 400 | 1.2 | Status bar text |

---

## Component Classes

### Console Frame
```css
.console-frame {
  background: var(--wf-bg);
  color: var(--wf-text);
  font-family: 'Courier New', monospace;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
```

### Surface Panel
```css
.surface-panel {
  background: var(--wf-surface);
  border: 1px solid var(--wf-border);
  padding: 16px;
  margin: 8px;
}
```

### Wireframe Header
```css
.wireframe-header {
  background: var(--wf-surface);
  border-bottom: 1px solid var(--wf-border);
  padding: 8px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 1px;
}
```

### Wireframe Footer
```css
.wireframe-footer {
  background: var(--wf-surface);
  border-top: 1px solid var(--wf-border);
  padding: 4px 16px;
  font-size: 11px;
  color: var(--wf-text-muted);
  display: flex;
  justify-content: space-between;
}
```

### Wireframe Sidebar
```css
.wireframe-sidebar {
  width: 240px;
  background: var(--wf-surface);
  border-right: 1px solid var(--wf-border);
  overflow-y: auto;
}
```

### Wireframe Content
```css
.wireframe-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}
```

### Wireframe Status Bar
```css
.wireframe-status {
  background: var(--wf-surface);
  border-top: 1px solid var(--wf-border);
  padding: 2px 16px;
  font-size: 11px;
  color: var(--wf-text-muted);
  display: flex;
  gap: 16px;
}
```

### Wireframe Command Line
```css
.wireframe-command {
  background: var(--wf-bg);
  border: 1px solid var(--wf-border);
  color: var(--wf-primary);
  font-family: 'Courier New', monospace;
  font-size: 14px;
  padding: 8px 12px;
  width: 100%;
  outline: none;
}
.wireframe-command:focus {
  border-color: var(--wf-primary);
}
```

---

## Effects

### Scanline Effect
```css
.scanline-effect {
  position: relative;
  overflow: hidden;
}
.scanline-effect::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 2px,
    rgba(0, 0, 0, 0.03) 2px,
    rgba(0, 0, 0, 0.03) 4px
  );
  pointer-events: none;
}
```

### Blinking Cursor
```css
@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}
.cursor-blink {
  animation: blink 1s step-end infinite;
}
```

### Terminal Typing
```css
@keyframes typing {
  from { width: 0; }
  to { width: 100%; }
}
.typing-effect {
  overflow: hidden;
  white-space: nowrap;
  animation: typing 2s steps(40, end);
}
```

---

## Layer Map (L300-L399 Surface)

| Layer | ID | Component | Description |
|-------|----|-----------|-------------|
| L300 | `wireframe:console` | ConsoleFrame | Root console frame |
| L301 | `wireframe:header` | WireframeHeader | Top header bar |
| L302 | `wireframe:sidebar` | WireframeSidebar | Left navigation |
| L303 | `wireframe:content` | WireframeContent | Main content area |
| L304 | `wireframe:status` | WireframeStatus | Bottom status bar |
| L305 | `wireframe:command` | WireframeCommand | Command input line |
| L306 | `wireframe:panel` | SurfacePanel | Generic surface panel |
| L307 | `wireframe:modal` | WireframeModal | Modal overlay |
| L308 | `wireframe:toast` | WireframeToast | Notification toast |
| L309 | `wireframe:menu` | WireframeMenu | Context menu |

---

## LENS Variables

```json
{
  "snack_box": {
    "console": {
      "title": "string",
      "status_text": "string",
      "command_history": "string[]",
      "current_command": "string",
      "show_scanlines": "boolean",
      "show_cursor": "boolean"
    },
    "panels": {
      "active_panel": "string",
      "panel_stack": "string[]",
      "sidebar_open": "boolean",
      "sidebar_width": "number"
    },
    "features": {
      "scanlines": "boolean",
      "crt_effect": "boolean",
      "grid_overlay": "boolean",
      "command_line": "boolean"
    }
  },
  "runtime": {
    "session_id": "string",
    "start_time": "ISO-8601",
    "uptime": "number",
    "memory_usage": "number",
    "active_surfaces": "string[]"
  }
}
```

---

## Deployment

### Docker Compose
```yaml
# docker-compose.wireframe.yml
version: '3.8'
services:
  wireframe:
    image: ucode4-wireframe:latest
    container_name: ucode4-wireframe
    ports:
      - "3003:3000"
    environment:
      - NODE_ENV=production
      - USX_SKIN_ID=wireframe-console-scaffold
      - USX_SURFACE_API=http://ucode-usx-router:3001
    networks:
      - ucode-network

networks:
  ucode-network:
    driver: bridge
```

### Environment Variables
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `USX_SKIN_ID` | Yes | `wireframe-console-scaffold` | Skin identifier |
| `USX_SURFACE_API` | Yes | — | USX router endpoint |
| `WF_SHOW_SCANLINES` | No | `true` | Enable scanline effect |
| `WF_SHOW_CURSOR` | No | `true` | Show blinking cursor |
| `WF_GRID_OVERLAY` | No | `false` | Show grid overlay |

---

## Related Documents

- `docs/themes/README.md` — Theme overview
- `docs/specs/WIREFRAME_SPEC.md` — Wireframe specification
- `surfaces/wireframe/` — Wireframe surface implementation
