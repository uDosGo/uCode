# Apps

The `apps/` root is the education-facing map for user-visible `uHOME` surfaces.
During Phase 1, the active server-side implementations still live in
`src/uhome_server/`.

Current app surfaces:

- `dashboard/` for household summary, health, and operator controls
- `tablet-kiosk/` for touch-first room and living-room control surfaces

Client apps remain separate repositories. This root describes the server-owned
app surfaces and contracts, not embedded mobile or TV clients.
