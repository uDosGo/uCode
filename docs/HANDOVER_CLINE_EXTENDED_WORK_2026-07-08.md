# Handover to Cline: Extended and Enhanced Coding Work

Date: 2026-07-08  
Repository: uDosGo/uCode  
Baseline commit already pushed: `942b593` (main)

## 1. Current Baseline

Recent sprint work delivered and pushed includes:

- Runtime bridge LENS registry wired for Repton, Elite, NetHack, Eamon.
- NetHack and Eamon LENS extractor modules created.
- Python 3.14 import path stabilized for runtime package loading in isolated venv (`.venv-amos-check`).
- Sprint and DEV plan status updated to match validated code/test outcomes.

This handover captures what still needs extended/enhanced implementation from earlier sprints.

## 2. Still Required (Carry-Over Backlog)

## A. Shared Runtime Extraction (Phase 2 pending)

Source of truth: `docs/DEV_PLAN.md` marks `shared/` as pending.

Required work:

- Audit duplicated runtime utilities across `runtimes/basic/` and `runtimes/amos/`.
- Extract stable common APIs into `shared/src/` with versioned interfaces.
- Replace direct duplicated logic with imports from `shared/` in both runtimes.
- Add tests that run against shared interfaces from both runtimes.

Acceptance criteria:

- At least one concrete common subsystem moved into `shared/` (not only helpers).
- Both `ucode1` and `ucode2` use shared package code in executable paths.
- Runtime tests pass after extraction with no behavior regression.

## B. Program Scaffold-to-Playable Upgrades

Multiple programs were completed as scaffold/skeleton in prior sprints but still need gameplay-depth coding.

### 1) uConstruct (highest remaining design debt)

Current state: scaffold only; tile editor/resource model remains design-phase.

Required work:

- Implement tile placement/edit loop and map persistence format.
- Implement resource definitions (tile types, costs, constraints).
- Add in-program validation for map bounds and layer consistency.
- Add minimal playable/editor workflow script and test harness.

Acceptance criteria:

- User can create/edit/save/load a tile map.
- Program roundtrip save/load retains all tile/layer metadata.

### 2) NetHack (beyond research + 52-line skeleton)

Current state: research + skeleton + LENS extractor.

Required work:

- Implement core turn loop and dungeon movement rules.
- Implement minimal combat and inventory interaction model.
- Wire gameplay state addresses to extractor fields with real values.
- Add deterministic tests for movement/combat transitions.

Acceptance criteria:

- A playable dungeon floor loop exists (move, inspect, combat, inventory).
- `LENS CAPTURE nethack` returns non-trivial live state reflecting gameplay transitions.

### 3) Eamon (beyond research + 63-line skeleton)

Current state: research + skeleton + LENS extractor.

Required work:

- Implement parser loop (`VERB NOUN`) with command normalization.
- Implement room graph traversal and item interactions.
- Implement basic combat and persistent player stats.
- Bind runtime state to LENS extractor for player/room/inventory snapshots.

Acceptance criteria:

- Playable command loop with navigation and interaction.
- `LENS CAPTURE eamon` reflects room/player changes during play.

### 4) Knight Orc and Apple Panic enhancement pass

Current state: both exist as skeleton-level implementations; Apple Panic has core digging/trapping mechanics.

Required work:

- Knight Orc: strengthen narrative progression + state management.
- Apple Panic: tune enemy behavior, scoring, and difficulty progression.
- Add regression tests for core mechanics and game-over/win paths.

Acceptance criteria:

- Both programs have repeatable play loops and verifiable progression states.

## C. Runtime Bridge Hardening

Recent fixes solved several split-module import issues; this should be completed as a full hardening pass.

Required work:

- Sweep all split modules for non-relative imports and unresolved symbol dependencies.
- Remove duplicate codegen artifacts (duplicate decorators/duplicated methods) where still present.
- Add import smoke tests for major runtime entrypoints under Python 3.12 and 3.14.

Acceptance criteria:

- `python -c "import ucode1, ucode2"` succeeds in supported venvs.
- No import-path failures from split modules in CI.

## D. Integration and E2E Confidence

Required work:

- Expand LENS integration tests beyond command-level success strings.
- Add assertions for key presence and semantic value changes after simulated actions.
- Add a small end-to-end workflow test: command dispatch -> state mutation -> capture snapshot.

Acceptance criteria:

- LENS tests verify meaningful state evolution, not only command response text.

## 3. Suggested Execution Order for Cline

1. Shared runtime extraction planning doc + first subsystem extraction.
2. Runtime bridge hardening sweep + import smoke tests.
3. uConstruct playable editor loop implementation.
4. NetHack core loop + tests + LENS live-state integration.
5. Eamon parser/room loop + tests + LENS live-state integration.
6. Knight Orc / Apple Panic enhancement pass.
7. Final integration test expansion and documentation refresh.

## 4. Operational Notes

- Use isolated venv for Python package validation; system Python is externally managed (PEP 668).
- Keep commits scoped by subsystem to simplify rollback.
- Unrelated working tree artifact observed previously: `gridsmith.code-workspace` deletion; do not accidentally mix unrelated workspace cleanup into feature commits.

## 5. Quick Validation Commands

```bash
# Runtime imports (venv)
python -c "import ucode1, ucode2"

# Runtime LENS tests
python -m pytest runtimes/basic/tests/test_lens_capture.py -q

# Workspace tests (as needed)
npm run test
```
