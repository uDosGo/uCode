# uCode Integration Reference

## Overview

uCode is the runtime + agent ecosystem for the uDos platform. It integrates
with uCore (backend), Hivemind (LLM), MCP servers (tools), OpenRouter (cloud models),
and Vault (state/secrets).

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     uCode Ecosystem                       │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐   │
│  │ uCore    │  │ Hivemind │  │ OpenRouter            │   │
│  │ (daemon) │  │ (LLM)    │  │ (cloud models)        │   │
│  └────┬─────┘  └────┬─────┘  └──────────┬───────────┘   │
│       │              │                   │               │
│       └──────┬───────┴───────────────────┘               │
│              │                                           │
│       ┌──────▼──────┐  ┌──────────┐  ┌──────────────┐   │
│       │ MCP Servers │  │ Vault    │  │ Secrets Store │   │
│       │ (tools)     │  │ (state)  │  │ (keys)        │   │
│       └─────────────┘  └──────────┘  └──────────────┘   │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

## Components

### 1. uCore (Backend Daemon)
- **Location:** `~/Code/uCore/`
- **Start:** `cd backend && python3 -m app`
- **Port:** 8484
- **Endpoints:** `/api/health`, `/api/surfaces/*`, `/api/feed/*`, `/api/skills/*`

### 2. Hivemind (LLM Provider)
- **Config:** `config/hivemind.env` → `~/.config/hivemind/.env`
- **Models:** OpenRouter (GLM-5.1, DeepSeek V4 Flash, Qwen 3.6 27B), local Ollama
- **Budget:** $20/month hard limit, $5 alert threshold
- **Log:** `~/.local/share/udos/costs/openrouter-usage.yaml`

### 3. OpenRouter (Cloud LLM Routing)
- **Config:** `config/openrouter.yaml`
- **Endpoint:** `https://openrouter.ai/api/v1`
- **Fallback Chain:** Ollama local → DeepSeek V4 Flash → GLM-5.1
- **Premium:** Claude Opus 4.5 (opt-in only, $15/1k tokens)

### 4. MCP Servers (Cline Tool Integration)
- **Config:** `config/mcp_config.json` → `~/.config/cline/mcp_config.json`
- **Servers:**
  | Server | Command | Purpose |
  |--------|---------|---------|
  | uCore | `python3 -m app` | Skills, surfaces, feed |
  | GridSmith | `node agents/gridsmith/dist/cli.js mcp` | World builder tools |
  | Hivemind | `python3 -m app.mcp.hivemind_server` | LLM knowledge layer |
  | Feed | `python3 -m app.mcp.feed.feed_server` | Activity ingestion |

### 5. Vault (State & Variables)
- **Config:** `config/vault.yaml`
- **Base Path:** `~/.local/share/udos/Vault/`
- **Variable Scopes:** user, global, snack, system
- **Secrets Store:** macOS Keychain / encrypted file

### 6. Secrets & Variables
- **API Keys:** OPENROUTER_API_KEY, ANTHROPIC_API_KEY, OPENAI_API_KEY, GITHUB_TOKEN
- **Store:** macOS Keychain (preferred) or `~/.local/share/udos/Vault/variables/`
- **Access Pattern:** `ucode var get <scope> <key>` / `ucode var set <scope> <key> <value>`

### 7. PyCharm IDE
- **Run Configs:** `.idea/runConfigurations/` — Basic Runtime, GridSmith CLI
- **Modules:** uCode (root), ucode1 (basic runtime), ucode2 (amos runtime)
- **Python Interpreter:** `~/Code/uCore/backend/.venv/bin/python`

## Quick Start

```bash
# 1. Copy API keys
cp config/hivemind.env ~/.config/hivemind/.env
chmod 600 ~/.config/hivemind/.env
# Edit and fill in your OpenRouter key

# 2. Install MCP config
cp config/mcp_config.json ~/.config/cline/mcp_config.json

# 3. Start uCore backend
cd ~/Code/uCore/backend && python3 -m app

# 4. Open workspace in PyCharm
open ucode.code-workspace
```

## File Map

| Path | Purpose |
|------|---------|
| `config/hivemind.env` | LLM API key template |
| `config/mcp_config.json` | MCP server registration |
| `config/vault.yaml` | State/secrets storage config |
| `config/openrouter.yaml` | Cloud model routing + budget |
| `docs/GRIDSMITH_DEV_PLAN.md` | GridSmith agent build plan |
| `docs/UCODE_RUNTIME_SPEC.md` | BBCSDL runtime spec |
| `.tasker/dev-flow.yaml` | Sprint task tracking |
| `.clinerules` | Cline agent rules |
| `devlog.yaml` | Dev activity log |