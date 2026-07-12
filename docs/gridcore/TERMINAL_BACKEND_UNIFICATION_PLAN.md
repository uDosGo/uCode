# uCode Terminal ↔ Backend Unification Plan

**Date**: 2026-07-12
**Status**: Planning — Phase A implementation in progress
**Sprint**: sprint.2026-07-12
**Scope**: Wire the uCode Terminal (OK> prompt) to the live Python backend runtime (gridcore_adapter.py → SessionState → BBCSDL), unify command dispatch, and document the complete command surface.

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         BROWSER (Frontend)                           │
│                                                                     │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────┐   │
│  │ TerminalPanel │    │ TeletextPanel│    │ GridCanvas / Editor  │   │
│  │  (80×24 or    │    │  (40×25)     │    │  (variable grid)    │   │
│  │   40×25 grid) │    │              │    │                      │   │
│  └──────┬───────┘    └──────┬───────┘    └──────────┬───────────┘   │
│         │                   │                        │               │
│         ▼                   ▼                        ▼               │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │              @udos/viewport-renderer                          │   │
│  │  TerminalWidget          TeletextWidget         GridEditor    │   │
│  │  ─ attaches keyboard     ─ renders pages       ─ cell edits   │   │
│  │  ─ DOM or Canvas view    ─ FASTEXT navigation  ─ layer mgmt   │   │
│  └──────────────┬────────────────────────────────────────────────┘   │
│                 │                                                    │
│                 ▼                                                    │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │              @udos/gridcore                                    │   │
│  │  TerminalSurface         TeletextSurface       Grid (algebra) │   │
│  │  ─ scrollback buffer    ─ page stack           ─ cells (x,y,z)│   │
│  │  ─ input line           ─ page provider        ─ transforms    │   │
│  │  ─ role colours         ─ mosaic blocks        ─ viewport calc │   │
│  │                          ─ FASTEXT links                        │   │
│  └──────────────┬────────────────────────────────────────────────┘   │
│                 │                                                    │
│                 ▼                                                    │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │              RuntimeBridge                                     │   │
│  │  ─ CommandDispatcher: (cmd) => { output, teletextPage? }      │   │
│  │  ─ Event bus: command-output, teletext-navigate, error        │   │
│  │  ─ Modes: in-process | websocket | (live python process)      │   │
│  │                                                               │   │
│  │  ★ Phase A adds: createProcessBridge() factory                │   │
│  │    → spawns Python gridcore_adapter.py via stdin/stdout       │   │
│  └──────────────┬──────────────────────────────────────────────┘   │
│                 │  JSON-RPC 2.0 over stdin/stdout                   │
│                 │  { "method":"dispatch","params":{"command":"X"} } │
│                 │  { "result": { "output":"...","teletextPage":? }} │
└─────────────────┼──────────────────────────────────────────────────┘
                  │
┌─────────────────┼──────────────────────────────────────────────────┐
│                 ▼  PYTHON BACKEND (gridcore_adapter.py)            │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │              gridcore_adapter.py                               │   │
│  │  ─ handle_request(): routes JSON-RPC methods                  │   │
│  │  ─ dispatch_command(): maps command strings → results         │   │
│  │  ─ load_teletext_page(n): loads/generates CEEFAX pages        │   │
│  │  ─ serve_http(port): optional HTTP + WebSocket server         │   │
│  └──────────────┬──────────────────────────────────────────────┘   │
│                 │                                                    │
│                 ▼                                                    │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │              SessionState (singleton)                          │   │
│  │  ─ grid: Grid(80, 24)           mutable cell grid             │   │
│  │  ─ worlds: Dict[str, WorldEntry] world registry               │   │
│  │  ─ program_lines: Dict[int, str]  loaded BASIC source         │   │
│  │  ─ program_filename: str | None   current program name        │   │
│  │  ─ active_world: str              selected world              │   │
│  │                                                               │   │
│  │  Methods: grid_set/get/render, world_create/list/switch,      │   │
│  │           program_load/list/save/cat, renum                   │   │
│  └──────────────┬──────────────────────────────────────────────┘   │
│                 │                                                    │
│                 ▼                                                    │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │              LENS Registry (7 programs)                        │   │
│  │  repton → repton_lens.py         elite → elite_lens.py        │   │
│  │  nethack → nethack_lens.py       eamon → eamon_lens.py        │   │
│  │  uconstruct → uconstruct_lens.py                               │   │
│  │  knight-orc → knight_orc_lens.py                               │   │
│  │  apple-panic → apple_panic_lens.py                             │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │              BBCSDL Bridge (bbcsdl_bridge.py)                  │   │
│  │  ─ BBCSDLProcess: spawn bbcsdl in headless mode               │   │
│  │  ─ PROGRAM_LOAD / PROGRAM_RUN via stdin pipe                  │   │
│  │  ─ Output capture via _read_loop thread                       │   │
│  │  ★ Triggered by: OK> RUN (after LOAD)                         │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Command Reference — Complete uCode Command Surface

The following 25 commands are available at the `OK>` prompt. After Phase A, all dispatch through `gridcore_adapter.py` → `SessionState`.

### 2.1 Core Commands

| Command | Syntax | Description | Implemented |
|---------|--------|-------------|:---:|
| `HELP` | `HELP` or `?` | List all available commands | ✅ live |
| `BEEP` | `BEEP` | Emit BEL character (ASCII 7) | ✅ live |
| `QUIT` | `QUIT` | Signal session end | ✅ live |

### 2.2 Grid Commands

| Command | Syntax | Description | Implemented |
|---------|--------|-------------|:---:|
| `GRID` | `GRID [HELP]` | Show grid subcommands | ✅ live |
| `GRID SET` | `GRID SET <col> <row> <char>` | Set cell character at position | ✅ live |
| `GRID GET` | `GRID GET <col> <row>` | Get cell character at position | ✅ live |
| `GRID SHOW` | `GRID SHOW` | ASCII render of current grid | ✅ live |

### 2.3 World Commands

| Command | Syntax | Description | Implemented |
|---------|--------|-------------|:---:|
| `WORLD` | `WORLD` or `WORLD LIST` | List all created worlds | ✅ live |
| `WORLD NEW` | `WORLD NEW <name>` | Create a new world (default 80×24) | ✅ live |
| `WORLD CREATE` | `WORLD CREATE <name>` | Alias for WORLD NEW | ✅ live |
| `WORLD SWITCH` | `WORLD SWITCH <name>` | Switch active world | ✅ live |

### 2.4 Program Commands (BBC BASIC)

| Command | Syntax | Description | Implemented |
|---------|--------|-------------|:---:|
| `CAT` | `CAT` or `DIR` | List available programs under `programs/` | ✅ live |
| `LOAD` | `LOAD <filename>` or `LOAD "<file>"` | Load a .bbc program into memory | ✅ live |
| `LIST` | `LIST [start[-end]]` | List loaded program lines | ✅ live |
| `RUN` | `RUN` | Execute loaded program via BBCSDL | ✅ live¹ |
| `SAVE` | `SAVE [filename]` | Save program lines to file | ✅ live |
| `NEW` | `NEW` | Clear program memory | ✅ live |
| `RENUM` | `RENUM [start [step]]` | Renumber program lines | ✅ live |

¹ `RUN` requires `bbcsdl` binary in `runtimes/basic/bbcsdl/`. Falls back to error message if not found.

### 2.5 Teletext / CEEFAX Commands

| Command | Syntax | Description | Implemented |
|---------|--------|-------------|:---:|
| `CEEFAX` | `CEEFAX` | Open Teletext at page 100 (Main Index) | ✅ live |
| `CEEFAX N` | `CEEFAX <page>` | Navigate to specific page (100–899) | ✅ live |

**Known pages:**
- 100 — Main Index
- 400 — Vault Configuration
- 888 — Help & About

### 2.6 Vault Commands

| Command | Syntax | Description | Implemented |
|---------|--------|-------------|:---:|
| `VAULT` | `VAULT` | Show vault key list | ✅ live |
| `VAULT <key>` | `VAULT ollama_endpoint` | Look up a vault key | ✅ live |

### 2.7 Ecosystem Commands

| Command | Syntax | Description | Implemented |
|---------|--------|-------------|:---:|
| `LAYER` | `LAYER [LIST]` | List grid layers | ✅ live |
| `MAP` | `MAP [LIST]` | List loaded maps | ✅ live |
| `UVOX` | `UVOX` | UVox spatial algebra engine status | ✅ live |
| `SKIN` | `SKIN` | List available visual themes | ✅ live |
| `LENS` | `LENS [HELP]` | List registered LENS programs | ✅ live |
| `LENS LIST` | `LENS LIST` | Enumerate LENS extractor programs | ✅ live |
| `LENS CAPTURE` | `LENS CAPTURE <program>` | Capture game state snapshot | ✅ live |
| `LENS RESTORE` | `LENS RESTORE <program>` | Restore game state | ✅ live |

### 2.8 GridSmith Commands (informational)

| Command | Syntax | Description | Implemented |
|---------|--------|-------------|:---:|
| `GRIDSMITH` | `GRIDSMITH [HELP]` | GridSmith agent tool reference | ✅ live |
| `GRIDSMITH TOOLS LIST` | — | List all 16 GridSmith tools | ✅ live |

---

## 3. Phase Plan

### Phase A — Live Runtime IPC ✅ (in progress)

**Goal**: Replace the mock `defaultDispatcher` with a live Python subprocess bridge.

**Tasks:**

| ID | Task | File | Status |
|----|------|------|:---:|
| A.1 | Add `createProcessBridge()` factory to RuntimeBridge | `packages/gridcore/src/bridge/runtime-bridge.ts` | ✅ |
| A.2 | Add `stopProcessBridge()` lifecycle method | `packages/gridcore/src/bridge/runtime-bridge.ts` | ✅ |
| A.3 | Verify Python dispatch works (HELP, LENS LIST, CAT, etc.) | `runtimes/basic/bridge/gridcore_adapter.py` | ☐ |
| A.4 | Create live Python bridge demo page | `packages/viewport-renderer/demo/index.html` | ✅ |
| A.5 | Build IIFE bundles for browser demo | `packages/gridcore/dist/`, `packages/viewport-renderer/dist/` | ☐ |
| A.6 | End-to-end manual test (OK> HELP → live Python response) | Manual | ☐ |
| A.7 | Unit test PythonProcessBridge with mock subprocess | `packages/gridcore/test/` | ☐ |

**Validation**: Type `HELP` at the terminal, receive the live Python backend's response (which differs from the mock — the Python backend returns "Commands: HELP BEEP RENUM GRID LAYER MAP WORLD VAULT CEEFAX UVOX SKIN LENS QUIT LOAD LIST RUN SAVE NEW CAT DIR").

### Phase B — Frontend Surface Integration

**Goal**: Replace the demo page's inline grid rendering with proper ViewportRenderer widgets, and integrate into the uCore frontend surface.

**Tasks:**

| ID | Task | File | Status |
|----|------|------|:---:|
| B.1 | Wire TerminalWidget to createProcessBridge auto-start | `TerminalWidget.ts` | ☐ |
| B.2 | Add to demo page: bridge status indicator, auto-fallback to mock | `demo/index.html` | ☐ |
| B.3 | Extract demo into reusable `ucode-terminal` page module | New file | ☐ |
| B.4 | Replace uCore's UCodeSurface TerminalPanel with TerminalWidget | `uCore frontend` | ☐ |
| B.5 | Replace uCore's TeletextGrid with TeletextWidget | `uCore frontend` | ☐ |
| B.6 | Verify render parity: terminal font, teletext flash, mosaic | Visual | ☐ |

### Phase C — Program Execution Loop

**Goal**: Full `LOAD → LIST → RUN` cycle through the Terminal, with program output appearing inline.

**Tasks:**

| ID | Task | File | Status |
|----|------|------|:---:|
| C.1 | Wire BBCSDL stderr/stdout capture to SessionState output buffer | `bbcsdl_bridge.py`, `gridcore_adapter.py` | ☐ |
| C.2 | Stream program output line-by-line through bridge events | `gridcore_adapter.py`, `runtime-bridge.ts` | ☐ |
| C.3 | Add `RUN` output rendering to TerminalSurface (live stream mode) | `terminal-surface.ts` | ☐ |
| C.4 | Test with each of 7 programs (LOAD → RUN → verify output) | Manual | ☐ |
| C.5 | Add `PROGRAM` command group (STOP, CONT, STEP — if BBCSDL supports) | `gridcore_adapter.py` | ☐ |

### Phase D — GridBuffer Round-Trip

**Goal**: When a program runs and modifies a Grid, the GridBuffer is streamed back to the frontend viewport for live visual rendering.

**Tasks:**

| ID | Task | File | Status |
|----|------|------|:---:|
| D.1 | Define `grid_update` JSON-RPC method on adapter | `gridcore_adapter.py` | ☐ |
| D.2 | Emit `grid-update` events from RuntimeBridge | `runtime-bridge.ts` | ☐ |
| D.3 | Wire GridEditor widget to `grid-update` events | `viewport-renderer` | ☐ |
| D.4 | Implement program → LENS-capture → GridBuffer projection | `lens.py`, adapter | ☐ |
| D.5 | Test: `LOAD eamon`, `RUN`, see dungeon map in grid editor | Manual | ☐ |

### Phase E — Teletext Data Sources

**Goal**: Wire Vault, doc-sites, and User Feeds into the Teletext page provider with real data (not hardcoded).

**Tasks:**

| ID | Task | File | Status |
|----|------|------|:---:|
| E.1 | Load vault.yaml at runtime and generate page 400 dynamically | `gridcore_adapter.py` | ✅ |
| E.2 | Add Markdown → Teletext page converter for doc-sites (page 500+) | New module | ☐ |
| E.3 | Create course catalogue page 300 from `seeds/course-registry.json` | `gridcore_adapter.py` | ☐ |
| E.4 | Add User Feed mappers (RSS/Atom → Teletext pages) | New module | ☐ |
| E.5 | Add CEEFAX page file format: `runtimes/basic/ceefax/pages/<n>.json` | Pages dir | ☐ |

---

## 4. Integration Wiring Diagram

```
User types "HELP" in browser
    │
    ▼
TerminalSurface.typeChar() → submit() → onCommand handler
    │
    ▼
RuntimeBridge.sendCommand("HELP")
    │
    ▼
CommandDispatcher("HELP")  ←─ set via setDispatcher() or constructor
    │
    ├─ [mock mode]    → defaultDispatcher() → { output: "Commands: HELP..." }
    │                    emitted as command-output event
    │
    └─ [live mode]    → PythonProcessBridge.dispatchCommand("HELP")
                         │
                         ▼
                      Write to stdin: {"jsonrpc":"2.0","method":"dispatch",
                                         "params":{"command":"HELP"},"id":"1"}
                         │
                         ▼  (Python subprocess)
                      gridcore_adapter.handle_request()
                         │
                         ▼
                      dispatch_command("HELP")
                         │
                         ▼
                      Returns {"output": "Commands: HELP BEEP...LOAD LIST RUN..."}
                         │
                         ▼
                      Write to stdout: {"jsonrpc":"2.0","id":"1","result":{...}}
                         │
                         ▼  (TypeScript)
                      PythonProcessBridge.handleStdout() → parse JSON
                         │
                         ▼
                      resolve({ output: "Commands: HELP BEEP...LOAD LIST..." })
                         │
                         ▼
                      RuntimeBridge sends result to emit('command-output', ...)
                         │
                         ▼
                      TerminalSurface.writeLine() → redraw() → grid changed
                         │
                         ▼
                      TerminalWidget.onDisplayChange → DOMViewport.render()
                         │
                         ▼
                      Browser shows: "Commands: HELP BEEP RENUM..."
```

### Teletext Navigation Wire Path

```
User types "CEEFAX 400"
    │
    ▼
dispatch_command("CEEFAX 400")
    │
    ▼
Returns {"output": "Loading page 400...", "teletextPage": 400}
    │
    ▼
RuntimeBridge.sendCommand() sees teletextPage
    │
    ▼
emit('teletext-navigate', 400)
    │
    ▼
teletextSurface.navigateTo(400)
    │
    ▼
TeletextPageProvider → load_teletext_page(400) → vault.yaml → TeletextPage
    │
    ▼
TeletextSurface writes page content to grid cells
    │
    ▼
TeletextWidget.onDisplayChange → DOMViewport.render()
    │
    ▼
CEEFAX page 400 visible in browser
```

---

## 5. File Inventory

### Source files being modified/created

```
packages/gridcore/src/
  bridge/
    runtime-bridge.ts          ★ Phase A: add createProcessBridge(), stopProcessBridge()
    python-process-bridge.ts   ★ Phase A: stabilize, add readiness check, error recovery
  terminal/
    terminal-surface.ts          Phase C: add live output streaming mode
  index.ts                       Re-export createProcessBridge

packages/viewport-renderer/src/
  widgets/
    TerminalWidget.ts            Phase B: add auto-bridge-start
    TeletextWidget.ts            Phase B: add page-load-from-backend flag
  demo/
    index.html                   ★ Phase A/B: live bridge demo page

runtimes/basic/bridge/
  gridcore_adapter.py            ★ Phase A-D: command dispatch, grid_state method, RUN output
  session_state.py               Phase C: program execution buffer
  bbcsdl_bridge.py               Phase C: output capture → SessionState

runtimes/basic/ceefax/
  pages/                         Phase E: JSON page files for teletext
```

---

## 6. Test Strategy

| Layer | What | Tool | When |
|-------|------|------|------|
| Unit | PythonProcessBridge spawn/mock | vitest (with mock child_process) | Phase A |
| Unit | gridcore_adapter dispatch_command (all 25 commands) | pytest | Phase A |
| Unit | SessionState grid/world/program ops | pytest | Phase A |
| Integration | RuntimeBridge → live Python → HELP response | vitest + subprocess | Phase A |
| Integration | TerminalSurface → RuntimeBridge → Python → output rendering | vitest + jsdom | Phase B |
| E2E | Demo page: type HELP, see live Python response | Playwright | Phase B |
| E2E | LOAD → LIST → RUN → see program output | Playwright | Phase C |
| E2E | CEEFAX 400 → Vault page renders | Playwright | Phase E |

---

## 7. Documentation Deliverables

| Document | Path | Status |
|----------|------|:---:|
| Terminal ↔ Backend Unification Plan (this file) | `docs/gridcore/TERMINAL_BACKEND_UNIFICATION_PLAN.md` | ✅ |
| uCode Command Reference (OK> prompt) | `docs/gridcore/OK_PROMPT_COMMAND_REFERENCE.md` | ☐ |
| Python Bridge Protocol Specification | `docs/gridcore/PYTHON_BRIDGE_PROTOCOL.md` | ☐ |
| Updated GridUI Rendering Contract | `docs/GRIDUI_RENDERING_CONTRACT.md` | Phase B |
| Developer Quick Start (run the terminal demo) | `docs/basic/QUICK_START.md` (update) | Phase B |

---

## 8. Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Python venv mismatch** — bridge spawns wrong Python version | Bridge won't start | Detect Python version at startup; fall back to mock |
| **BBCSDL binary not found** — `RUN` fails | Broken program execution | Graceful error: "BBCSDL not installed" |
| **Large program output floods terminal** — e.g., infinite loop | Browser tab freeze | Timeout (30s default), output line cap (500 lines) |
| **SessionState is singleton** — multiple browser tabs share state | State confusion | Per-session keying (future); document as known limitation |
| **GridBuffer serialization overhead** — 80×24 grid at 30fps | Performance drop | Delta-encoding, diff-only updates (Phase D) |

---

## 9. Success Criteria

1. User opens demo page, clicks "Start Live Python Bridge", types `HELP` — receives live Python dispatch response
2. `CEEFAX 400` navigates to Vault page with real data from `config/vault.yaml`
3. `CAT` lists the 7 programs under `programs/`
4. `LOAD repton/src/repton.bbc` loads and `LIST` shows source
5. `LENS LIST` enumerates all 7 registered LENS extractors
6. `GRID SET 5 5 X` and `GRID GET 5 5` work with persistent SessionState
7. All existing tests continue to pass (307+) with no regressions
8. Bridge gracefully falls back to mock dispatcher if Python process crashes