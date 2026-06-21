# Clients

This repository defines server contracts for downstream `uHOME` clients, but it
does not own those client implementations.

Expected downstream client lanes:

- Android tablet or phone control surfaces
- Google TV style playback surfaces
- Apple TV or tvOS style playback surfaces

Rules:

- stable server APIs belong here
- client-native UX and packaging belong in separate repos
- kiosk and dashboard contracts may be documented here even when no local UI is
  embedded in this repo

Current client contracts:

- `PLAYBACK-API.md` - playback status, handoff, and queue APIs
- `LAUNCHER-API.md` - launcher session lifecycle APIs
- `HOUSEHOLD-API.md` - household-safe browse and status APIs
- `BEACON-ACTIVATE.md` - Wizard-offered local Wi-Fi portal into curated offline
  vault content
- `CLIENT-CAPABILITIES.md` - controller/remote/touch capability model
- `INTEGRATION-GUIDE.md` - end-to-end integration guide for client teams
