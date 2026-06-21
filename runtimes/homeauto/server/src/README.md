# Source Package

`src/` is the active implementation root for the current runtime package.

Phase 1 keeps the package here on purpose:

- `pyproject.toml` entrypoints already target `src/uhome_server/`
- tests and runtime boot paths expect the current package layout
- moving code now would add churn without improving ownership clarity

Rule:

- use `apps/`, `modules/`, `services/`, `vault/`, and `courses/` as the public
  teaching language
- keep implementation changes inside `src/uhome_server/` until a move produces
  a cleaner ownership boundary

Phase 2 note:

- `src/uhome_server/installer/` is now the neutral public import surface for
  install planning, staging, promotion, and host-apply flows
- `src/uhome_server/sonic/` remains in place as the deprecated compatibility
  and legacy import layer during the boundary cleanup
- repo-local code should not add new imports from `uhome_server.sonic`
