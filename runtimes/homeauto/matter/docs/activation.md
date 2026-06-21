# uHOME-matter Activation

## Purpose

This document marks the first active implementation tranche for
`uHOME-matter`.

The activation goal is to make the Matter extension lane teachable,
checkable, and ready for implementation without broadening ownership beyond:

- Matter integration contracts
- Home Assistant bridge assets
- clone-definition assets for compatible local adapters
- local automation example flows
- lightweight contract validation for this repo

## Activated Surfaces

- `src/` as the integration contract lane
- `src/matter-clone-catalog.json` as the clone-definition lane
- `src/home-assistant-bridge-definition.json` as the shared bridge definition
  for the server runtime
- `scripts/run-uhome-matter-checks.sh` as the repo validation entrypoint
- `tests/` as the extension contract validation lane
- `config/` as the checked-in integration config lane
- `examples/basic-matter-bridge.json` as the smallest integration example
- `examples/basic-home-assistant-clone.json` as the smallest clone example
- `config/bridge-targets.example.json` as the starter target registry
- `docs/server-runtime-handoff.md` as the server-to-extension ownership map
- `docs/release-policy.md` and `CHANGELOG.md` as release discipline surfaces

## Current Validation Contract

Run:

```bash
scripts/run-uhome-matter-checks.sh
```

This command:

- verifies the required repo entry surfaces exist
- checks that the sample integration contracts are structurally valid
- checks that the clone catalog and target registry are structurally valid
- rejects private local-root path leakage in tracked repo docs and scripts

## Boundaries

This activation does not move ownership into `uHOME-matter` for:

- `uHOME-server` runtime services
- `uHOME-client` runtime-profile contracts
- canonical runtime semantics
- remote sync or publishing behavior
