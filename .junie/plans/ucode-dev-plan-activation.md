---
sessionId: session-260705-223438-1lcl
isActive: true
---

# Requirements平衡性设计

### Overview & Goals
The goal is to transition from the setup phase to active implementation of the Phase 1 core packages and Phase 2 runtime migration. Specifically, this involves building the GridSmith core class, expanding its CLI capabilities, and scaffolding the new BBCSDL-based Python runtime bridge.

### Scope
- **In Scope**:
    - Implementation of the `GridSmith` core class in `@udos/gridsmith`.
    - Expansion of the GridSmith CLI to support all defined tools.
    - Scaffolding of the `runtimes/basic/bridge/` and `runtimes/basic/bbcsdl/` directories.
    - Initial unit tests for GridSmith.
- **Out of Scope**:
    - Full implementation of LENS/SKIN state extraction (Phase 2, later tasks).
    - Production release of the `.runtime` nugget format.


# Technical Design

### Current Implementation
The repository is currently in the "setup" phase. Core packages are built and have basic tests. AI integration (Ollama/OpenRouter) is configured and verified. Documentation for repository boundaries and runtime specifications is present and locked.

### Key Decisions
1. **Python Runtime**: Pin to **Python 3.12.12** for all uCode runtime development. Higher versions (3.13, 3.14) are reserved for system tools only, due to keepalive/socket regressions identified during setup.
2. **AI Provider Routing**: **Ollama** (qwen2.5-coder:3b) is the primary local provider. **OpenRouter** serves as a paid fallback. All routing is handled via uCore's snackbar daemon.
3. **Dependency Architecture**: Strict one-way flow: `gridcore` -> `viewport-renderer` -> `gridsmith`. No internal package may depend on host application code (uCore).

### Proposed Changes
1. **GridSmith Core Class**: Implement a central `GridSmith` class in `agents/gridsmith/src/index.ts` that encapsulates tool operations and grid management.
    - Class signature (methods to implement):
        - `public createGrid(cols: number, rows: number, cellSize?: number)`
        - `public editCell(gridId: string, x: number, y: number, layer: number, data: object)`
        - `public composeLayers(gridId: string, layers: number[])`
        - `public async importBasicProgram(programOrPath: string, worldName: string)`
        - `public async importAmosProgram(programOrPath: string, worldName: string)`
        - `public async exportUVox(gridId: string, outputPath: string)`
        - `public latLonToUCode(lat: number, lon: number, level?: number)`
        - `public uCodeToLatLon(coord: string)`
    - This class will bridge the low-level functions in `@udos/gridcore` with the agent-facing tool definitions.
2. **CLI Expansion**: Update `agents/gridsmith/src/cli.ts` to provide a robust command-line interface for world-building, importing, and location conversion.
3. **BBCSDL Scaffolding**: Create the initial directory structure for the v2 BBCSDL runtime bridge (`runtimes/basic/bridge/`) and prepare for engine binary packaging.
4. **Testing Infrastructure**: Add Vitest-based unit tests for the GridSmith core class in `agents/gridsmith/src/index.test.ts`.

### File Structure
- `docs/DEV_PLAN.md`: Primary development roadmap.
- `.tasker/dev-flow.yaml`: Active task tracking.
- `devlog.yaml`: Milestone tracking.
- `scripts/setup-ai-integration.sh`: Environment verification tool.


# Testing

### Validation Approach
- **GridSmith Core**: Successful build and execution of unit tests using `npm run test` in `agents/gridsmith`.
- **CLI Functionality**: Manual verification of `gridsmith grid create` and `gridsmith location` commands via CLI.
- **Runtime Readiness**: Verification of the existence of the `runtimes/basic/bridge` directory and the initial `bbcsdl_bridge.py` scaffold.


# Delivery Steps

###   Step 1: GridSmith Core Class & Unit Testing
Implement the `GridSmith` class to provide a unified interface for uCode tools.
- Create the `GridSmith` class in `agents/gridsmith/src/index.ts`.
- Integrate all `GRIDSMITH_TOOLS` definitions into class methods (some may be stubs).
- Add `agents/gridsmith/src/index.test.ts` with Vitest coverage for core grid creation and location conversion.
- Ensure `@udos/gridsmith` builds correctly with `npm run build`.

###   Step 2: CLI Expansion & Tool Integration
Update the CLI to use the core class and expose full world-building functionality.
- Refactor `agents/gridsmith/src/cli.ts` to instantiate and use the `GridSmith` class.
- Add CLI support for `import-amos`, `edit-cell`, and `export-uvox` commands.
- Implement robust argument parsing and JSON output formatting.
- Verify CLI execution via `node agents/gridsmith/dist/cli.js`.

###   Step 3: BBCSDL Runtime Scaffolding
Establish the foundation for the new Python-based BBCSDL runtime bridge.
- Create `runtimes/basic/bridge/` and `runtimes/basic/bbcsdl/` directories.
- Scaffold `runtimes/basic/bridge/bbcsdl_bridge.py` with the initial `BBCSDLRuntime` class.
- Update `devlog.yaml` to reflect the start of the Phase 2 migration.