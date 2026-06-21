---
title: "Home Assistant Container — Provisioning Summary"
status: draft
last_updated: 2026-04-22T23:26:13+10:00
category: documentation
tags: [ai, assist, home-assistant, iot, ucode3]
description: "Status: migrated into `uHOME Server`"
---
# Home Assistant Container — Provisioning Summary

Status: migrated into `uHOME Server`
Updated: 2026-03-07

## Scope

The Home Assistant gateway was migrated from `uDOS/wizard/services/home_assistant/`
into this repository as:

- `src/uhome_server/services/home_assistant/`
- `library/home-assistant/container.json`
- `library/home-assistant/bridge.json`

## Delivered Surfaces

- REST API gateway under `/api/ha`
- WebSocket gateway under `/ws/ha`
- device registry and discovery scaffolding
- service-call bridge surface
- manifest-driven library/container runtime entry

## Remaining Work

- real Home Assistant token and server configuration
- production auth integration
- richer device discovery and type-specific handlers
- operational packaging and deployment hardening
