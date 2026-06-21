# Home Assistant Container Gateway — uHOME Server

This is the standalone `uHOME` copy of the Home Assistant gateway service that
previously lived under `uDOS/wizard/services/home_assistant/`.

## Purpose

Provide a REST and WebSocket gateway for Home Assistant integration as a
first-class `uHOME` library/container runtime.

## Runtime

- service module: `uhome_server.services.home_assistant`
- module entry point: `python3 -m uhome_server.services.home_assistant`
- default port: `8765`
- health endpoint: `/health`
- REST base: `/api/ha`
- WebSocket endpoint: `/ws/ha`

## Main Components

- `service.py` — app lifecycle and service wiring
- `gateway/manager.py` — gateway state and event orchestration
- `api/rest.py` — REST endpoints
- `api/websocket.py` — real-time update channel
- `devices.py` — registry, discovery, and control scaffolding
- `schemas/` — gateway, device, and entity schemas

## Notes

- this remains a scaffolded gateway rather than a fully integrated production
  Home Assistant control plane
- `library/home-assistant/container.json` is the manifest-driven runtime entry
  used by the `uHOME` library/container subsystem
