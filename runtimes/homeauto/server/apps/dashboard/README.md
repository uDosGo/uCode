# Dashboard

Purpose:

- household health and summary surface
- library, network, and bridge status overview
- operator-facing view of server readiness

Current runtime anchors:

- `src/uhome_server/routes/dashboard.py`
- `docs/ui/UHOME-DASHBOARD.md`

Planned direction:

- keep the server summary contract here
- allow a dedicated dashboard UI to grow without changing the repo boundary
