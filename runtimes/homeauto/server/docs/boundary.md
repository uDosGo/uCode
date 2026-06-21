# uHomeNest — runtime boundary

## Owns

- always-on local services
- scheduling and persistence
- automation fulfillment
- home/server infrastructure modules
- Linux host runtime for uHOME
- Thin GUI and kiosk-style local presentation contracts
- local vault reader and Beacon Activate content surfaces
- base runtime profiles and household host configuration

## Does Not Own

- canonical parsing and execution rules
- browser operator workflow UX
- provider bridge adapters
- Google Docs, Google Keep, Google Tasks, or HubSpot sync orchestration
- Apple-native sync or iCloud handling
- long-term Matter clone definitions or Home Assistant extension contracts

## v2 Runtime Rule

`uHomeNest` is the durable local runtime that remains available when Wizard
is not open.

It may:

- execute scheduled or queued local jobs
- host nearby output and Beacon-adjacent surfaces
- expose minimal household-safe or kiosk-safe status views
- report results and events back into shared workflow state

It should not become the owner of online assist policy or conscious workflow
advancement semantics.

`uHomeNest` should consume the shared handoff artifacts from:

- `uDOS-core/contracts/automation-job-contract.json`
- `uDOS-core/contracts/automation-result-contract.json`
- `uDOS-core/contracts/workflow-state-contract.json`
