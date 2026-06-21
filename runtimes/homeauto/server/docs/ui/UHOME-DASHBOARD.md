# uHOME Dashboard Surface

The old `uDOS/wizard/dashboard/src/routes/UHome.svelte` route is now treated as
an external consumer of this repo’s API, not as the owner of `uHOME` runtime
state.

## Canonical API Inputs

The dashboard surface for `uHOME` should consume:

- `GET /api/dashboard/summary`
- `GET /api/dashboard/health`
- `GET /api/platform/uhome/status`
- `POST /api/platform/uhome/presentation/start`
- `POST /api/platform/uhome/presentation/stop`
- `GET /api/ha/status`
- `GET /api/ha/discover`
- `POST /api/ha/command` with `uhome.playback.status`

## Ownership Rule

- UI implementations may live in separate frontend repos or downstream apps
- runtime ownership stays in this server repo
- the dashboard is a client of the `uHOME` API surface, not the source of truth
