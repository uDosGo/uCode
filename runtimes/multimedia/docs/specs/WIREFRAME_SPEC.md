---
title: "Wireframe Console Scaffold Specification v1.0.0"
status: draft
last_updated: 2026-05-17T00:14:16+10:00
category: specification
tags: [specification, ucode4]
description: "**Updated:** 2026-05-16"
---
# Wireframe Console Scaffold Specification v1.0.0

**Status:** Active
**Updated:** 2026-05-16
**Theme ID:** `wireframe-console-scaffold`
**Skin ID:** `wireframe-skin`
**Layer:** L300-L399 (Surface Layer)

---

## 1. Purpose

This spec defines the Wireframe console scaffold theme for uCode4. The Wireframe theme provides a minimal, monochrome base layer for all uCode4 surfaces — a clean, low-fidelity wireframe that prioritizes structure over decoration.

## 2. Theme Contract

### 2.1 Identity

| Field | Value |
|-------|-------|
| `skin.id` | `wireframe-console-scaffold` |
| `version` | `1.0.0` |
| `framework` | Tailwind CSS |
| `inherits` | `usx://themes/monochrome` |

### 2.2 Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| Tailwind CSS | 3.x | Utility classes |
| Courier New | system | Monospace font |
| SF Mono | system | Fallback monospace |

## 3. Color Tokens

| Token | Hex | CSS Variable | Description |
|-------|-----|-------------|-------------|
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

## 4. Typography

| Level | Font | Size | Weight | Line Height |
|-------|------|------|--------|-------------|
| Body | Courier New | 14px | 400 | 1.4 |
| Heading 1 | Courier New | 24px | 700 | 1.2 |
| Heading 2 | Courier New | 20px | 600 | 1.3 |
| Heading 3 | Courier New | 16px | 600 | 1.3 |
| Code | Courier New | 13px | 400 | 1.4 |
| Caption | Courier New | 12px | 400 | 1.3 |
| Status | Courier New | 11px | 400 | 1.2 |

## 5. Component Classes

| Component | CSS Class | Description |
|-----------|-----------|-------------|
| Console Frame | `.console-frame` | Root layout container |
| Surface Panel | `.surface-panel` | Generic panel container |
| Header | `.wireframe-header` | Top header bar |
| Footer | `.wireframe-footer` | Bottom footer bar |
| Sidebar | `.wireframe-sidebar` | Left navigation panel |
| Content | `.wireframe-content` | Main content area |
| Status Bar | `.wireframe-status` | Bottom status indicators |
| Command Line | `.wireframe-command` | Command input field |

## 6. Effects

| Effect | CSS Class | Description |
|--------|-----------|-------------|
| Scanline | `.scanline-effect` | CRT scanline overlay |
| Blinking Cursor | `.cursor-blink` | Terminal cursor blink |
| Typing | `.typing-effect` | Typewriter text animation |
| Hover | `brightness-110` | Brightness increase on hover |
| Focus | `ring-1 ring-primary` | Focus ring |
| Active | `brightness-90` | Brightness decrease on active |

## 7. Layer Map (L300-L399)

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

## 8. LENS Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `snack_box.console.title` | string | "uCode4" | Console window title |
| `snack_box.console.status_text` | string | "READY" | Status bar text |
| `snack_box.console.command_history` | string[] | [] | Command history |
| `snack_box.console.current_command` | string | "" | Current input |
| `snack_box.console.show_scanlines` | boolean | true | Scanline toggle |
| `snack_box.console.show_cursor` | boolean | true | Cursor toggle |
| `snack_box.panels.active_panel` | string | "" | Active panel ID |
| `snack_box.panels.panel_stack` | string[] | [] | Panel navigation stack |
| `snack_box.panels.sidebar_open` | boolean | true | Sidebar visibility |
| `snack_box.panels.sidebar_width` | number | 240 | Sidebar width in px |
| `snack_box.features.scanlines` | boolean | true | Scanline feature flag |
| `snack_box.features.crt_effect` | boolean | false | CRT effect flag |
| `snack_box.features.grid_overlay` | boolean | false | Grid overlay flag |
| `snack_box.features.command_line` | boolean | true | Command line flag |
| `runtime.session_id` | string | — | Session identifier |
| `runtime.start_time` | ISO-8601 | — | Session start time |
| `runtime.uptime` | number | 0 | Session uptime in seconds |
| `runtime.memory_usage` | number | 0 | Memory usage in MB |
| `runtime.active_surfaces` | string[] | [] | Active surface IDs |

## 9. Acceptance Criteria

- [ ] Console frame renders with correct background color
- [ ] Surface panels display with proper borders and padding
- [ ] Header shows title and navigation elements
- [ ] Footer shows status information
- [ ] Sidebar toggles open/closed
- [ ] Command line accepts input
- [ ] Scanline effect renders correctly
- [ ] Blinking cursor animation works
- [ ] Typing animation works
- [ ] Color tokens apply correctly across all components
- [ ] Monospace typography renders consistently
- [ ] LENS variables update correctly
- [ ] Layer map components render at correct layers
- [ ] Responsive layout works on mobile

## 10. Related Documents

- `docs/themes/WIREFRAME_THEME.md` — Full theme documentation
- `docs/themes/README.md` — Theme overview
- `surfaces/wireframe/` — Wireframe surface implementation
