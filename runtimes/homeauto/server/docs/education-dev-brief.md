# uHomeNest — education structure refactor brief

*Former filename:* `uHOME-server-education-dev-brief.md`.

## Objective
Refactor the **uHOME** server pathway in this monorepo to serve as the **home infrastructure pathway within the uDOS ecosystem** while becoming a learning environment for building local‑network services.

uHOME teaches developers how to build:

- LAN infrastructure
- home media servers
- automation systems
- local‑first network services

---

# Strategic Positioning

uHOME becomes:

**The home infrastructure module family for uDOS.**

It runs on Linux and powers:

- media systems
- device automation
- LAN service networks
- tablet kiosk dashboards

---

# Proposed Repository Structure

```
uHOME-server/
  apps/
  modules/
  services/
  vault/
  docs/
  courses/
  scripts/
  config/
  tests/
```

### apps

```
apps/
  dashboard/
  tablet-kiosk/
  admin/
```

Interfaces for household control.

### modules

```
modules/
  media/
  dvr/
  home-ops/
  steam-surface/
  home-assistant-bridge/
```

Modules represent installable home infrastructure features.

### services

```
services/
  playback/
  scheduling/
  launcher/
  lan-discovery/
  automation/
```

Services power the home network runtime.

### vault

Markdown database describing home state.

```
vault/
  homes/
  rooms/
  devices/
  schedules/
  media/
  notes/
```

Example:

```
devices/living-room-tv.md
rooms/lounge.md
```

This enables:

- Obsidian compatibility
- editable home infrastructure
- transparent system state

---

# uHOME Learning Path

## Course 01 – Local Network Systems

Topics:

- LAN architecture
- service discovery
- device management

Project:
Define home network vault.

---

## Course 02 – Media Infrastructure

Topics:

- media servers
- playback systems
- streaming architecture

Project:
Create media service module.

---

## Course 03 – Home Automation

Topics:

- event automation
- scheduling
- smart device control

Project:
Implement automation workflows.

---

## Course 04 – Multi‑Device Systems

Topics:

- Android tablet kiosks
- TV clients
- distributed household nodes

Project:
Deploy multi‑device uHOME system.

---

# Integration with uDOS

uHOME consumes:

- uDOS vault schema patterns
- module activation system
- shared service architecture

uHOME represents **one pathway inside the larger ecosystem**.

---

# Implementation Tasks

1. Introduce Markdown vault schema
2. Modularize services into feature modules
3. Add structured course path
4. Provide example household configurations
5. Add LAN topology documentation

---

# Expected Outcome

uHOME becomes:

- reference architecture for home infrastructure
- education system for LAN development
- modular home automation platform