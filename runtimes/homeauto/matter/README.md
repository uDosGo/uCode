# uHOME-matter (`matter/` in uHomeNest)

This package lives at **`matter/`** inside the **[uHomeNest](../README.md)** monorepo (standalone repo was **`uHOME-matter`**).

## Purpose

Matter and Home Assistant integration for **uHOME**: bridge contracts, device
maps, and adapter assets so the **controller-first kiosk / thin UX** on
`uHOME-server` can show **real home automation state** (entities, scenes, rooms)
alongside media and games—not a bolt-on only for a wider uDOS command-centre.

## Ownership

- Matter-facing extension contracts
- Home Assistant bridge surfaces
- local automation integration notes and examples
- validation for repo-owned setup and contract assets

## Non-Goals

- base `uHOME-server` runtime ownership
- shared client-runtime ownership
- canonical runtime semantics owned by `uDOS-core`
- online CRM or host-local WordPress operator surfaces (outside the uHOME stream)

## Spine

- `src/`
- `docs/`
- `tests/`
- `scripts/`
- `config/`
- `examples/`

## Family Relation

`uHOME-matter` extends the **uHOME product** with automation **contracts** and
bridge definitions; `uHOME-server` **renders** operator-facing thin UI that
consumes those assets.

Split:

- **`uHOME-server`** — always-on runtime, kiosk/thin presentation, media, LAN
  services, automation job fulfilment **on the host**
- **`uHOME-matter`** — Matter, Home Assistant, clone/target maps, bridge JSON
- **`uHOME-client` + apps** — clients; server + matter stay source of truth

## Repo Setup Surface

The scaffold includes:

- `src/matter-bridge-contract.json` as the baseline extension contract
- `src/matter-clone-catalog.json` as the checked-in lane for clone targets and
  adapter profiles
- `src/home-assistant-bridge-definition.json` as the shared bridge definition
  consumed by the server runtime
- `examples/basic-matter-bridge.json` as the smallest Matter bridge example
- `examples/basic-home-assistant-clone.json` as the smallest Home Assistant
  clone mapping example
- `config/bridge-targets.example.json` as the starter local target registry
- `docs/server-runtime-handoff.md` as the runtime boundary handoff from
  `uHOME-server`
- `docs/release-policy.md` and `CHANGELOG.md` for release discipline

## Activation

The v2 repo activation path is documented in `docs/activation.md`.

Run the current repo validation entrypoint with:

```bash
scripts/run-uhome-matter-checks.sh
```
