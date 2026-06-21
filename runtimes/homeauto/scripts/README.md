# Scripts

The `scripts/` root is reserved for checked-in operational tooling for **uHomeNest**
(**v3.9.x**) / the uHOME server runtime.

Current state:

- most deployment and install mechanics still live in `src/uhome_server/sonic/`
- generated host-apply scripts are produced during installer execution

Boundary rule:

- generic deployment bootstrap should converge toward
  `sonic-screwdriver`
- **uHomeNest** should keep only server-owned scripts and host-role helpers

Current validation entrypoint:

- `run-uhome-server-checks.sh` for editable install bootstrap and repo test
  execution
- `first-run-launch.sh` for direct local server plus console/kiosk launch
- `first-run-launch.command` as the macOS wrapper for the launcher script
