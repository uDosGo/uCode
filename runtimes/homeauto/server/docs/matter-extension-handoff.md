# uHomeNest → uHOME-matter handoff

This document closes the active v2 gap between the server runtime and the
Matter automation lane.

## uHomeNest keeps

- host lifecycle and persistent execution
- scheduling and service composition
- local bridge execution endpoints and health checks
- installer and runtime toggles for optional bridge support

## `uHOME-matter` Owns

- Matter bridge contracts
- Home Assistant adapter definitions
- clone catalogs and bridge-target maps
- local automation examples and extension-facing docs

## Transitional Rule

If a change defines what a local automation target is, how it is mapped, or
which adapter profile it uses, it belongs in `uHOME-matter`.

If a change defines how the server starts, supervises, probes, or exposes that
integration at runtime, it belongs in **uHomeNest** (`server/`).
