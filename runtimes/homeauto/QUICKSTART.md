# uHomeNest Quickstart (v1.0.0)

<<<<<<< HEAD
Bring up a fresh local stream stack with Jellyfin + minimal API + USXD browser surface.

## 1) Install

```bash
./scripts/install.sh
```

## 2) Start services

```bash
./scripts/start.sh
```

## 3) Health check
=======
This quickstart gets the local runtime running and validates the first Wizard
and Empire handoff seams.

## Prerequisites

- Python 3.9+
- Git
- optional sibling repos for the paired flow: `../uDOS-wizard` and `../uDOS-empire`

## 1. Bootstrap And Validate

From the repo root:
>>>>>>> develop

```bash
./scripts/healthcheck.sh
curl -sS http://127.0.0.1:7890/api/health
```

Expected response:

```json
{"status":"ok"}
```

## 4) Stop services

```bash
./scripts/stop.sh
```

## 5) Add media

<<<<<<< HEAD
- Add files under `~/media/` using the structure described in `docs/MEDIA_VAULT.md`.
- Re-run the scanner/indexer entrypoint once media changes are made.
=======
## 2. Run The API

From the repo root (after `~/.udos/venv/uhome-server` exists):

```bash
cd /path/to/uHOME-server
source ~/.udos/venv/uhome-server/bin/activate
python -m uvicorn uhome_server.app:app --host 127.0.0.1 --port 8000 --reload
```

Use any free port you like (`--port 7890`, etc.). **All URLs below assume the port you chose** — here **`8000`**.

Base URL:

- `http://127.0.0.1:8000`

## 3. Smoke Test Core Routes

In another terminal:

```bash
curl http://127.0.0.1:8000/api/health
curl http://127.0.0.1:8000/api/runtime/ready
curl http://127.0.0.1:8000/api/runtime/info
curl http://127.0.0.1:8000/api/household/status
curl http://127.0.0.1:8000/api/launcher/status
```

**Thin UI (browser proof for Cursor workspace 03):** open these on the same host/port:

- `http://127.0.0.1:8000/api/runtime/thin/automation` — automation status HTML
- `http://127.0.0.1:8000/api/runtime/thin/read` — default **prose** reading page
- `http://127.0.0.1:8000/api/runtime/thin/browse?rel=pathway/README.md` — sample `docs/` file

Confirm **`/static/thin/prose.css`** loads (Network tab or view source). If CSS is missing, build it under `thin-prose-build/` per `CHANGELOG.md`.

## 4. Pair Wizard To The Running Server

From the sibling `uDOS-wizard` repo:

```bash
python3 -m pip install --upgrade pip
python3 -m pip install -e .
UHOME_SERVER_URL=http://127.0.0.1:8000 python3 -m wizard.main
```

Then verify the bridge from another terminal:

```bash
curl http://127.0.0.1:8787/uhome/bridge/status
curl http://127.0.0.1:8787/uhome/automation/status
```

If both repos are checked out side by side, `udos-wizard-demo` from
`uDOS-wizard` also launches the paired stack automatically.

## 5. Dispatch An Empire Pack Into The Live Runtime

From the sibling `uDOS-empire` repo:

```bash
bash scripts/run-empire-checks.sh
python3 scripts/smoke/pack_preview.py --json --pack quickstart --execution-brief
python3 scripts/smoke/pack_run.py --json --pack quickstart --uhome-url http://127.0.0.1:8000 --write-default-report
```

Use `uDOS-empire/docs/quickstart.md` for the live Wizard and automation
bridge probes after the local runtime is up.

## 6. Useful CLI Commands

```bash
source ~/.udos/venv/uhome-server/bin/activate
uhome launcher status
uhome contracts sync-record
uhome backup list
```

## Next Docs

- `docs/getting-started.md` for the repo entry sequence
- `FIRST-TIME-INSTALL.md` for clean-machine setup
- `docs/DEPLOYMENT-GUIDE.md` for Ubuntu service deployment
- `docs/operations/README.md` for runbooks and operational recovery
>>>>>>> develop
