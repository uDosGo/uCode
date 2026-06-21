# Tablet Kiosk

Purpose:

- touch-first household control surface
- room-safe launcher and status views
- living-room and wall-panel style presentation

Current runtime anchors:

- `src/uhome_server/routes/platform.py`
- `src/uhome_server/services/uhome_presentation_service.py`
- `docs/decisions/v1-5-3-UHOME-KIOSK.md`

Planned direction:

- keep kiosk control contracts in this repo
- keep device-specific client implementations in separate downstream repos
