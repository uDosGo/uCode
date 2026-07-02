# uCode — uDosGo Runtime and Code Delivery

uCode is a self-contained runtime, grid algebra, and code-delivery repo for
uDosGo code surfaces. It is designed to be consumed by host applications such as
[uCore](https://github.com/uDosGo/uCore) without requiring those hosts to own
uCode internals.

**uCode is not a full application GUI.** It provides runtime packages, grid/code
algebra, import/export tooling, CLI/MCP surfaces, and inspectable render targets
such as terminal and teletext widgets.

---

## Repository Boundary

### uCode Owns

| Area                         | Role                                               |
| ---------------------------- | -------------------------------------------------- |
| `packages/gridcore`          | Grid algebra, code addressing, cell/layer model    |
| `packages/viewport-renderer` | Browser render surfaces, Terminal/Teletext widgets |
| `agents/gridsmith`           | CLI/MCP/import/export/build tooling                |
| `runtimes/basic`             | BASIC runtime bridge/package                       |
| `runtimes/amos`              | AMOS runtime bridge/package                        |
| `shared`                     | Cross-runtime support (not host-app-specific)      |
| `config/`                    | AI routing, MCP definitions, vault config          |
| `docs/`                      | Specs, boundary docs, workflows                    |
| `tests/`                     | Integration tests                                  |

### Host Applications (e.g. uCore) Own

- Product shell and navigation
- Developer dashboard/application GUI
- Workspace orchestration
- User/session/application state
- Long-running command-centre behaviour

uCore and other hosts should consume uCode through **package, CLI, MCP, or
runtime artifact boundaries**.

---

## Structure

```
uCode/
├── packages/
│   ├── gridcore/             Grid algebra and core grid/code primitives
│   └── viewport-renderer/    Terminal/teletext/browser render surfaces
├── agents/
│   └── gridsmith/            CLI, MCP, and import/export tooling
├── runtimes/
│   ├── basic/                BASIC runtime bridge/package
│   └── amos/                 AMOS runtime bridge/package
├── shared/                   Cross-runtime support
├── config/                   AI routing, MCP, vault configuration
├── docs/                     Specs, boundary docs, workflows
├── tests/                    Integration tests
└── README.md                 This file
```

Note: `homeauto` and `multimedia` runtimes have been moved to the
[HomeNest](https://github.com/uDosGo/HomeNest) repository.

---

## Quick Start

```bash
# Install and build all packages
npm install
npm run build
npm test

# Python runtime environment
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
```

---

## Package Boundaries

uCode packages are published under the `@udos` scope and are independently
versioned:

```typescript
import { ... } from '@udos/gridcore'
import { TerminalWidget, TeletextWidget } from '@udos/viewport-renderer'
import { GridSmith } from '@udos/gridsmith'
```

Dependency direction is strictly one-way:

```
@udos/gridcore          ← no internal deps
@udos/viewport-renderer → depends on @udos/gridcore
@udos/gridsmith         → depends on @udos/gridcore, @udos/viewport-renderer
```

No package depends on uCore or any host application.

---

## Runtime Inspection

uCode can expose runtime output through inspectable surfaces such as terminal
and teletext widgets. These are **render/inspection targets**, not the full
application GUI.

Browser-facing widgets live under:

```
packages/viewport-renderer/
```

Runtime and terminal inspection utilities live under:

```
runtimes/
```

---

## AI Integration

uCode provides MCP tooling (via GridSmith) that can be consumed by AI agents.
For full AI provider routing (Ollama, OpenRouter, Hivemind), uCode delegates to
uCore's snackbar daemon:

```
GridSmith MCP → uCore Snackbar (port 8484) → LiteLLM → Ollama/OpenRouter
```

Configuration lives in `config/`:

| File                     | Purpose                         |
| ------------------------ | ------------------------------- |
| `config/hivemind.env`    | API keys for OpenRouter, Ollama |
| `config/openrouter.yaml` | Model routing tiers & costs     |
| `config/mcp_config.json` | MCP server definitions          |
| `config/vault.yaml`      | Vault/secret paths              |

## Embedding uCode

uCode provides core functionality as standalone browser-embeddable bundles.

```bash
# Serve embeddables at http://localhost:8000
npm run serve:embed
```

See [`docs/EMBEDDING.md`](docs/EMBEDDING.md) for details.

---

## Development Rule

> **uCode must be installable, buildable, testable, and packageable from this
> repo alone. It must not depend on implementation code from uCore.**

See [`docs/UCODE_REPO_BOUNDARY.md`](docs/UCODE_REPO_BOUNDARY.md) for the full
boundary specification.
