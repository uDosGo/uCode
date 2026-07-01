# uCode / uCore Development Workspace

This VS Code workspace is configured for development across the uCode and uCore repositories.

## Workspace Structure

The workspace includes the following folders:

| Folder | Path | Description |
|--------|------|-------------|
| uCode (root) | `/Users/fredbook/Code/uCode` | uCode monorepo (frontend, packages, tests) |
| gridcore | `/Users/fredbook/Code/uCode/packages/gridcore` | Pure grid algebra core |
| viewport-renderer | `/Users/fredbook/Code/uCode/packages/viewport-renderer` | Viewport rendering |
| shared | `/Users/fredbook/Code/uCode/shared` | Shared utilities |
| runtimes | `/Users/fredbook/Code/uCode/runtimes` | Runtime environments |
| uCore | `/Users/fredbook/Code/uCore` | uCore backend |
| HomeNest | `/Users/fredbook/Code/HomeNest` | Home automation console |

## Quick Start

### Open Workspace
```bash
code /Users/fredbook/Code/uCode/ucode.code-workspace
```

### Available Tasks

Open the Command Palette (Cmd+Shift+P) and run "Tasks: Run Task" to see available tasks:

- **uCode: Build All** - Build all packages
- **uCode: Build gridcore** - Build gridcore package
- **uCode: Dev gridcore** - Start gridcore in watch mode
- **uCode: Test All** - Run all tests
- **uCode: Test gridcore** - Run gridcore tests
- **uCode: Start Frontend Dev Server** - Start Vite dev server
- **uCore: Start Backend** - Start Python backend server

### Debug Configurations

Open the Debug view (Cmd+Shift+D) to see available configurations:

- **Python: Current File (uCore)** - Debug current Python file
- **Python: Backend Server** - Debug backend server
- **Node: gridcore** - Run gridcore tests with vitest
- **Node: Attach to vitest** - Attach debugger to vitest

## Project Structure

```
~/Code/uCode/
├── frontend/           # React frontend
│   ├── src/
│   │   └── surfaces/   # Surface components
│   └── vite.config.ts
├── packages/
│   ├── gridcore/       # Grid algebra core
│   └── viewport-renderer/
├── shared/             # Shared code
├── runtimes/           # Runtime environments
├── tests/              # Test files
└── package.json        # Monorepo config

~/Code/uCore/
├── backend/            # Python backend
│   └── app/
└── ...

~/Code/HomeNest/
└── console/            # Home automation console
```

## Cross-Repository Aliases

The frontend uses path aliases configured in `vite.config.ts`:

- `@udos/gridcore` → `uCode/packages/gridcore/src/index.ts`
- `@udos/viewport-renderer` → `uCode/packages/viewport-renderer/src/index.ts`
- `@uCode3/*` → `uCode3/*` (if exists)
- `@HomeNest/*` → `HomeNest/*`

## Recommended Extensions

The workspace recommends these extensions (auto-install on open):

### Python
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- Black Formatter (ms-python.black-formatter)
- Flake8 (ms-python.flake8)

### TypeScript/JavaScript
- Prettier (esbenp.prettier-vscode)
- ESLint (ms-vscode.vscode-eslint)
- TypeScript Next (ms-vscode.vscode-typescript-next)

### General
- GitHub Copilot (github.copilot)
- GitLens (gitlens)
- Path Intellisense (ChristianKohler.PathIntellisense)
- Auto Rename Tag (formulahendry.auto-rename-tag)

## Settings

The workspace includes optimized settings for:

- **Formatting**: Prettier (TS/JS), Black (Python)
- **Linting**: Flake8 (Python), ESLint (TS/JS)
- **Editor**: Format on save, word wrap, rulers at 80/100/120
- **Terminal**: zsh with cursor blinking

## Environment Notes

- Python interpreter: `/Users/fredbook/Code/uCore/backend/.venv/bin/python`
- Node.js: Workspace uses npm workspaces
- Port configuration: Frontend dev server uses port 5173 (configurable via VITE_PORT env)