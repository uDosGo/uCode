# uHOME-matter Architecture

`uHOME-matter` provides the local automation and device-integration extension
lane for the `uHOME` family.

## Main Areas

- `src/` stores integration contract assets
- `config/` stores checked-in bridge-target examples
- `examples/` shows starter Matter and Home Assistant flows
- `docs/` explains ownership and setup
- `scripts/run-uhome-matter-checks.sh` is the activation validation entrypoint

Shared runtime-consumed assets in `src/` now include the Home Assistant bridge
definition used by `uHOME-server` for bridge metadata and command exposure.

## Contract Edges

- `uHOME-server` owns the always-on local runtime
- `uHOME-server` keeps any existing in-repo bridge implementations only as
  transitional runtime support until the dedicated `uHOME-matter` contract lane
  fully absorbs them
- `uHOME-client` and app repos consume shared runtime contracts but do not own
  Matter integration
- `uDOS-core` remains the canonical owner of workflow and command semantics
