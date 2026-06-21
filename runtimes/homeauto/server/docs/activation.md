# uHomeNest activation (uHOME server)

## Purpose

This document marks the first active implementation tranche for
**uHomeNest** (**v3.9.x**).

The activation goal is to make the server runnable, testable, and teachable as
the always-on local-service runtime without broadening its ownership beyond:

- persistent local services
- scheduling and recurrence
- home/server infrastructure modules
- operator-facing install and runtime checks for server-owned surfaces

## Activated Surfaces

- `src/uhome_server/app.py` as the current FastAPI runtime entrypoint
- `src/uhome_server/cli.py` as the local operator command lane
- `tests/` as the server validation lane
- `scripts/run-uhome-server-checks.sh` as the repo validation entrypoint
- `examples/basic-uhome-server-session.md` as the smallest operator walkthrough

## Current Validation Contract

Run:

```bash
scripts/run-uhome-server-checks.sh
```

This command:

- bootstraps a local `~/.udos/venv/uhome-server` runtime only when needed
- installs the editable dev dependencies
- runs the current `pytest` suite for the active server package

## Boundaries

This activation does not move ownership into **uHomeNest** for:

- canonical runtime semantics
- shell interaction ownership
- provider bridge ownership
- packaging bootstrap ownership outside server-specific runtime and install
  checks
