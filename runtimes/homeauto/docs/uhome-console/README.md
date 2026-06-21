---
title: "uHome Console — Complete Design Specification Sheet"
status: draft
last_updated: 2026-05-20T22:32:12+10:00
category: readme
tags: [homenest, ucode3, uhome]
description: "| Property               | Value                                                 |"
---
# uHome Console — Complete Design Specification Sheet

## 📋 Document Control

| Property               | Value                                                 |
| ---------------------- | ----------------------------------------------------- |
| **Theme Name**         | uHome Console                                         |
| **Version**            | 1.0.0                                                 |
| **Base OS**            | Ubuntu 22.04 LTS (Minimal) + Xorg                     |
| **Design Language**    | Apple TV + Google TV (10-foot UI)                     |
| **Underlying Desktop** | Ubuntu (GNOME) with Classic Modern styling            |
| **Navigation**         | Game controller (primary), mouse/keyboard (secondary) |
| **OBF Source**         | `uhome-console.obf` (v1)                              |
| **Last Updated**       | 2026-04-21                                            |

***

## 🎯 1. Core Philosophy

**uHome Console is a 10-foot interface for the living room, with a full Ubuntu desktop hidden beneath for admin and development.**

````
uHome Console
├── Console UI (Primary) → 10-foot, controller-first, card-based
├── Admin Desktop (Secondary) → Ubuntu GNOME + Classic Modern
└── Shared → uHomeNest services, sonic-express bridge
````

***

## 🎨 2. Colour Palette

### 2.1 Primary Colours (Dark Base)

| Role                 | Hex       | RGB         | Usage                        |
| -------------------- | --------- | ----------- | ---------------------------- |
| **Background**       | `#0A0A0A` | 10,10,10    | Main backdrop, deep black    |
| **Surface**          | `#1A1A1A` | 26,26,26    | Cards, panels, dialogs       |
| **Surface Elevated** | `#242424` | 36,36,36    | Hover states, selected cards |
| **Border**           | `#333333` | 51,51,51    | Subtle dividers              |
| **Text Primary**     | `#FFFFFF` | 255,255,255 | All primary text             |
| **Text Secondary**   | `#A0A0A0` | 160,160,160 | Subtitles, metadata          |

### 2.2 Accent Colours (Vibrant, 10-foot visible)

| Role               | Hex       | RGB        | Usage                   |
| ------------------ | --------- | ---------- | ----------------------- |
| **Primary Accent** | `#3A7BD5` | 58,123,213 | Focus ring, active card |
| **Accent Glow**    | `#5B9AE5` | 91,154,229 | Hover glow, selection   |
| **Success**        | `#2E7D32` | 46,125,50  | Confirmation, online    |
| **Warning**        | `#F57C00` | 245,124,0  | Alerts, attention       |
| **Error**          | `#C62828` | 198,40,40  | Errors, offline         |

### 2.3 Card Type Colours

| Role             | Hex       | RGB      | Usage             |
| ---------------- | --------- | -------- | ----------------- |
| **Media Card**   | `#1E1E2E` | 30,30,46 | Movies, TV, music |
| **App Card**     | `#2E1E2E` | 46,30,46 | Applications      |
| **Device Card**  | `#1E2E2E` | 30,46,46 | IoT devices       |
| **Setting Card** | `#2E2E1E` | 46,46,30 | Settings          |

### 2.4 Contrast Rules (10-foot visibility)

```css
/* Minimum contrast ratio for 10-foot viewing: 7:1 */
/* All text meets WCAG AAA at 4 feet distance */

/* Glow effect for focus (visible across room) */
.focus-glow {
  box-shadow: 0 0 0 3px #3A7BD5, 0 0 0 6px rgba(58,123,213,0.3);
}
```

***

## 📝 3. Typography System (10-Foot Optimised)

### 3.1 Font Families

| Role         | Font Stack       | Fallback   | Size (default) | Weight |
| ------------ | ---------------- | ---------- | -------------- | ------ |
| **Headline** | Inter, system-ui | sans-serif | 48px           | 700    |
| **Title**    | Inter, system-ui | sans-serif | 32px           | 600    |
| **Body**     | Inter, system-ui | sans-serif | 18px           | 400    |
| **Caption**  | Inter, system-ui | sans-serif | 14px           | 400    |
| **Button**   | Inter, system-ui | sans-serif | 20px           | 500    |
| **Status**   | Monaspace Neon   | monospace  | 14px           | 400    |

### 3.2 Font Sizes (10-Foot Scale)

| Element            | Size | Line Height | Viewing Distance |
| ------------------ | ---- | ----------- | ---------------- |
| Hero title         | 56px | 1.2         | 10-15 feet       |
| Section title      | 32px | 1.3         | 10 feet          |
| Card title         | 24px | 1.4         | 10 feet          |
| Card subtitle      | 16px | 1.4         | 8 feet           |
| Body text          | 18px | 1.5         | 8 feet           |
| Button text        | 20px | 1.3         | 10 feet          |
| Status bar         | 14px | 1.4         | 12 feet          |
| Toast notification | 16px | 1.4         | 10 feet          |

### 3.3 Typography Rules

```css
/* High contrast, no text shadows */
body {
  -webkit-font-smoothing: antialiased;
  text-shadow: none;
  letter-spacing: -0.01em;
}

/* Headlines tighter tracking */
h1, h2, h3 {
  letter-spacing: -0.02em;
}

/* Focus visible text (white on blue) */
:focus-visible {
  color: #FFFFFF;
}
```

***

## 🔲 4. Card System (Primary Navigation)

### 4.1 Card Specifications

| Property          | Value                      |
| ----------------- | -------------------------- |
| **Background**    | `#1A1A1A`                  |
| **Border Radius** | 16px                       |
| **Border**        | 1px solid `#333333`        |
| **Shadow**        | 0 8px 24px rgba(0,0,0,0.4) |
| **Padding**       | 16px                       |
| **Gap**           | 20px                       |

### 4.2 Card States

```css
/* Default card */
.card {
  background: #1A1A1A;
  border: 1px solid #333333;
  border-radius: 16px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

/* Hover (controller/mouse) */
.card:hover {
  transform: scale(1.02);
  border-color: #3A7BD5;
}

/* Focused (active card on screen) */
.card:focus-visible,
.card.active {
  outline: none;
  border: 3px solid #3A7BD5;
  transform: scale(1.05);
  box-shadow: 0 0 0 4px rgba(58,123,213,0.3), 0 12px 32px rgba(0,0,0,0.5);
}

/* Selected (pressed) */
.card:active {
  transform: scale(0.98);
}
```

### 4.3 Card Variants

```css
/* Media card (movies, TV) */
.card-media {
  background: linear-gradient(135deg, #1E1E2E, #161622);
  min-width: 280px;
  min-height: 380px;
}

/* App card */
.card-app {
  background: linear-gradient(135deg, #2E1E2E, #261626);
  min-width: 200px;
  min-height: 200px;
}

/* Device card */
.card-device {
  background: linear-gradient(135deg, #1E2E2E, #162626);
  min-width: 240px;
  min-height: 160px;
}

/* Setting card */
.card-setting {
  background: linear-gradient(135deg, #2E2E1E, #262616);
  min-width: 200px;
  min-height: 120px;
}
```

***

## 🧭 5. Layout & Navigation

### 5.1 Screen Layout

````
┌────────────────────────────────────────────────────────────────────────────┐
│  STATUS BAR (top)                                                          │
│  [Time] [Network] [Battery] [User]                      [Notifications]   │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │  HERO SECTION (featured content)                                      │ │
│  │  ┌────────────┐                                                       │ │
│  │  │            │  Title                                               │ │
│  │  │   Image    │  Description                                         │ │
│  │  │            │  [Play] [Details]                                    │ │
│  │  └────────────┘                                                       │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│                                                                            │
│  SECTION TITLE: Continue Watching                                         │
│  ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐                               │
│  │    │ │    │ │    │ │    │ │    │ │    │                               │
│  │ 🎬 │ │ 🎬 │ │ 🎬 │ │ 🎬 │ │ 🎬 │ │ 🎬 │                               │
│  │    │ │    │ │    │ │    │ │    │ │    │                               │
│  └────┘ └────┘ └────┘ └────┘ └────┘ └────┘                               │
│                                                                            │
│  SECTION TITLE: Apps                                                       │
│  ┌────┐ ┌────┐ ┌────┐ ┌────┐                                              │
│  │ 📱 │ │ 🎮 │ │ 📺 │ │ ⚙️ │                                              │
│  │App1│ │App2│ │App3│ │App4│                                              │
│  └────┘ └────┘ └────┘ └────┘                                              │
│                                                                            │
│  SECTION TITLE: Devices                                                    │
│  ┌────┐ ┌────┐ ┌────┐                                                     │
│  │ 💡 │ │ 🔥 │ │ 🚪 │                                                     │
│  │Light│ │Therm│ │Lock│                                                     │
│  └────┘ └────┘ └────┘                                                     │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
````

### 5.2 Grid System

```css
/* 12-column grid for 4K (3840px) */
.grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 20px;
  padding: 24px 48px;
}

/* Row spacing */
.row {
  margin-bottom: 40px;
}

/* Horizontal scroll rows (for large libraries) */
.row-scrollable {
  overflow-x: auto;
  scrollbar-width: thin;
  display: flex;
  gap: 20px;
  padding-bottom: 16px;
}

.row-scrollable::-webkit-scrollbar {
  height: 8px;
}
```

***

## 🎮 6. Controller Navigation

### 6.1 Button Mapping

| Controller         | Keyboard     | Mouse       | Action                 |
| ------------------ | ------------ | ----------- | ---------------------- |
| D-Pad / Left Stick | Arrow Keys   | Move        | Navigate between cards |
| A Button           | Enter        | Click       | Select / Activate      |
| B Button           | Escape       | Right-click | Back / Cancel          |
| X Button           | Space        | -           | Play / Pause           |
| Y Button           | Tab          | -           | Context menu           |
| LB / RB            | Q / E        | -           | Scroll rows / Sections |
| LT / RT            | Page Up/Down | -           | Jump sections          |
| Start              | S            | -           | Settings / Menu        |
| Select             | H            | -           | Help / Shortcuts       |

### 6.2 Focus Management

```javascript
// Focus indicator (visible across room)
.focus-indicator {
  position: absolute;
  pointer-events: none;
  border: 3px solid #3A7BD5;
  border-radius: 18px;
  box-shadow: 0 0 0 4px rgba(58,123,213,0.3), 0 0 0 8px rgba(58,123,213,0.1);
  transition: all 0.15s ease-out;
  z-index: 1000;
}

// Focus animation (subtle pulse)
@keyframes focusPulse {
  0%, 100% { box-shadow: 0 0 0 0px rgba(58,123,213,0.5); }
  50% { box-shadow: 0 0 0 8px rgba(58,123,213,0.2); }
}

.card.active {
  animation: focusPulse 2s infinite;
}
```

### 6.3 Navigation Grid

```css
/* Visible navigation grid (debug only) */
.navigation-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 4px;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 999;
}

/* Controller navigation order */
[data-nav-order] {
  order: attr(data-nav-order);
}
```

***

## 🔘 7. Component Specifications

### 7.1 Hero Banner

```css
.hero {
  background: linear-gradient(90deg, #1A1A1A 0%, #242424 50%, #1A1A1A 100%);
  border-radius: 24px;
  margin-bottom: 40px;
  overflow: hidden;
  position: relative;
}

.hero-content {
  padding: 48px;
  max-width: 60%;
}

.hero-title {
  font-size: 48px;
  font-weight: 700;
  margin-bottom: 16px;
  background: linear-gradient(135deg, #FFFFFF, #A0A0A0);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.hero-description {
  font-size: 18px;
  color: #A0A0A0;
  margin-bottom: 24px;
  line-height: 1.5;
}

.hero-buttons {
  display: flex;
  gap: 16px;
}

.hero-image {
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  width: 40%;
  object-fit: cover;
  opacity: 0.6;
}
```

### 7.2 Buttons (10-Foot)

```css
.button {
  padding: 12px 28px;
  border-radius: 40px;
  font-size: 18px;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: transform 0.1s ease;
}

.button-primary {
  background: #3A7BD5;
  color: #FFFFFF;
}

.button-primary:hover,
.button-primary:focus-visible {
  background: #5B9AE5;
  transform: scale(1.05);
}

.button-secondary {
  background: rgba(255,255,255,0.1);
  color: #FFFFFF;
  border: 1px solid #333333;
}

.button-secondary:hover,
.button-secondary:focus-visible {
  background: rgba(255,255,255,0.2);
  transform: scale(1.05);
}

.button:active {
  transform: scale(0.98);
}
```

### 7.3 Modal Dialog

```css
.modal {
  background: #1A1A1A;
  border: 1px solid #333333;
  border-radius: 24px;
  padding: 32px;
  min-width: 400px;
  max-width: 90vw;
  box-shadow: 0 24px 48px rgba(0,0,0,0.5);
}

.modal-overlay {
  background: rgba(0,0,0,0.8);
  backdrop-filter: blur(8px);
}

.modal-title {
  font-size: 28px;
  font-weight: 600;
  margin-bottom: 16px;
}

.modal-body {
  font-size: 18px;
  color: #A0A0A0;
  margin-bottom: 24px;
}

.modal-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
}
```

### 7.4 Toast Notification

```css
.toast {
  background: #242424;
  border-left: 4px solid #3A7BD5;
  border-radius: 12px;
  padding: 16px 24px;
  min-width: 300px;
  animation: slideIn 0.3s ease;
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 2000;
}

.toast-success {
  border-left-color: #2E7D32;
}

.toast-error {
  border-left-color: #C62828;
}

.toast-warning {
  border-left-color: #F57C00;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
```

### 7.5 Context Menu (Controller-Accessible)

```css
.context-menu {
  background: #1A1A1A;
  border: 1px solid #333333;
  border-radius: 12px;
  padding: 8px 0;
  min-width: 200px;
  z-index: 1500;
}

.context-menu-item {
  padding: 12px 20px;
  font-size: 16px;
  color: #FFFFFF;
  cursor: pointer;
}

.context-menu-item:hover,
.context-menu-item:focus-visible {
  background: #3A7BD5;
}

.context-menu-divider {
  height: 1px;
  background: #333333;
  margin: 8px 0;
}
```

***

## 🖥️ 8. Ubuntu Admin Desktop (Underlying)

### 8.1 Desktop Configuration

```yaml
# Ubuntu GNOME with Classic Modern styling
desktop:
  enabled: true
  switch_key: "Ctrl+Alt+F7"  # Console on F1-F6
  theme: "Classic Modern"     # Inherits from main spec
  
  panels:
    - position: top
      height: 32px
      autohide: false
      background: "#0A0A0A"
      
  dock:
    enabled: true
    position: left
    autohide: true
    background: "#1A1A1A"
    
  windows:
    border_radius: 0px
    shadows: none
    animations: false
```

### 8.2 Admin Desktop Styling (Dark/Flat)

```css
/* Ubuntu GNOME override for admin mode */
.admin-desktop {
  background: #0A0A0A;
}

/* Nautilus file manager */
.nautilus-window {
  background: #1A1A1A;
}

.nautilus-sidebar {
  background: #0A0A0A;
  border-right: 1px solid #333333;
}

/* Terminal */
.terminal-window {
  background: #0A0A0A;
  color: #FFFFFF;
}

.terminal-window .terminal-cursor {
  background: #3A7BD5;
}
```

### 8.3 Switching Between Modes

```bash
# Switch to admin desktop
sonic console switch --mode=desktop

# Switch to console UI
sonic console switch --mode=console

# Toggle with controller (hold Start + Select for 3 seconds)
```

***

## 🎬 9. Loading & Transitions

### 9.1 Loading Spinner (10-Foot Visible)

```css
.loader {
  width: 64px;
  height: 64px;
  border: 4px solid #333333;
  border-top-color: #3A7BD5;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* Skeleton loading for cards */
.card-skeleton {
  background: linear-gradient(90deg, #1A1A1A 0%, #242424 50%, #1A1A1A 100%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
```

### 9.2 Page Transitions

```css
/* Fade transition between sections */
.page-enter {
  opacity: 0;
  transform: translateY(20px);
}

.page-enter-active {
  opacity: 1;
  transform: translateY(0);
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.page-exit {
  opacity: 1;
}

.page-exit-active {
  opacity: 0;
  transition: opacity 0.2s ease;
}
```

***

## 🎨 10. Tailwind CSS Configuration

```javascript
// tailwind.config.js
module.exports = {
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        'console': {
          'bg': '#0A0A0A',
          'surface': '#1A1A1A',
          'elevated': '#242424',
          'border': '#333333',
          'text': '#FFFFFF',
          'text-secondary': '#A0A0A0',
          'accent': '#3A7BD5',
          'accent-hover': '#5B9AE5',
        },
        'card': {
          'media': '#1E1E2E',
          'app': '#2E1E2E',
          'device': '#1E2E2E',
          'setting': '#2E2E1E',
        }
      },
      fontFamily: {
        'sans': ['Inter', 'system-ui', 'sans-serif'],
        'mono': ['Monaspace Neon', 'monospace'],
      },
      fontSize: {
        '10ft-hero': '56px',
        '10ft-title': '32px',
        '10ft-body': '18px',
        '10ft-caption': '14px',
      },
      spacing: {
        '18': '72px',
        '22': '88px',
      },
      borderRadius: {
        'xl': '16px',
        '2xl': '24px',
      },
      animation: {
        'pulse-slow': 'pulse 2s infinite',
        'focus-pulse': 'focusPulse 2s infinite',
      },
      keyframes: {
        focusPulse: {
          '0%, 100%': { boxShadow: '0 0 0 0px rgba(58,123,213,0.5)' },
          '50%': { boxShadow: '0 0 0 8px rgba(58,123,213,0.2)' },
        }
      }
    }
  }
}
```

***

## 🎮 11. Controller UI Components

### 11.1 Controller Connection Indicator

```css
.controller-status {
  position: fixed;
  bottom: 16px;
  left: 16px;
  background: #1A1A1A;
  border-radius: 32px;
  padding: 8px 16px;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
  z-index: 100;
}

.controller-status.connected {
  border-left: 3px solid #2E7D32;
}

.controller-status.disconnected {
  border-left: 3px solid #C62828;
}
```

### 11.2 Button Hints (Bottom Bar)

```css
.button-hints {
  position: fixed;
  bottom: 16px;
  right: 16px;
  display: flex;
  gap: 16px;
  background: rgba(0,0,0,0.6);
  backdrop-filter: blur(8px);
  border-radius: 32px;
  padding: 8px 16px;
  z-index: 100;
}

.button-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #A0A0A0;
}

.button-hint-key {
  background: #333333;
  border-radius: 8px;
  padding: 4px 8px;
  font-family: monospace;
  font-size: 10px;
  color: #FFFFFF;
}
```

***

## 📡 12. Integration with uHomeNest

### 12.1 Device Status Cards

```css
.device-card {
  position: relative;
  overflow: hidden;
}

.device-status {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.device-status.online {
  background: #2E7D32;
  box-shadow: 0 0 0 2px rgba(46,125,50,0.3);
}

.device-status.offline {
  background: #C62828;
}

.device-status.warning {
  background: #F57C00;
}
```

### 12.2 Scene Activation

```css
.scene-card {
  background: linear-gradient(135deg, #3A7BD5, #1A5BB5);
}

.scene-card:active {
  transform: scale(0.98);
}

/* Scene activation animation */
.scene-active {
  animation: sceneFlash 0.5s ease;
}

@keyframes sceneFlash {
  0%, 100% { box-shadow: 0 0 0 0 rgba(58,123,213,0); }
  50% { box-shadow: 0 0 0 16px rgba(58,123,213,0.5); }
}
```

***

## ✅ 13. Compliance Checklist

| Element               | Spec                           | Status |
| --------------------- | ------------------------------ | ------ |
| 10-foot viewing       | 48px+ headlines, high contrast | ✅     |
| Controller navigation | D-pad, A/B/X/Y, triggers       | ✅     |
| Card focus            | 3px accent border + glow       | ✅     |
| Dark theme            | #0A0A0A base, #1A1A1A surface  | ✅     |
| Ubuntu desktop        | GNOME + Classic Modern         | ✅     |
| Tailwind styling      | Custom config                  | ✅     |
| Transitions           | Fade, scale, pulse             | ✅     |
| Loading states        | Skeleton + spinner             | ✅     |
| Device integration    | uHomeNest API ready            | ✅     |

***

## 📦 14. Installation Artifacts

```bash
# Console UI installation
/opt/uhome-console/
├── index.html
├── css/
│   ├── console.css
│   ├── tailwind.css
│   └── controller.css
├── js/
│   ├── navigation.js
│   ├── controller.js
│   └── uhome-api.js
└── assets/
    ├── images/
    ├── fonts/
    └── sounds/

# Admin desktop theme
/usr/share/themes/Classic-Modern-Admin/

# Session switching
/usr/local/bin/console-switch
```

***

## 🚀 14. Launch Commands

```bash
# Start console UI (fullscreen, controller-ready)
sonic console start --ui=uhome --fullscreen

# Switch to admin desktop
sonic console desktop --mode=admin

# Pair controller
sonic console pair --controller=bluetooth

# Test navigation (simulate controller)
sonic console simulate --nav=grid
```

***

**uHome Console delivers a 10-foot, controller-first smart home interface with full Ubuntu admin capabilities beneath — Apple TV meets Classic Modern flatness.**