# uHOME Console Launch Path

This runbook captures the launchable end-to-end console runtime path for v2.1 Round C.

## Prerequisites

- Python 3.9+
- local repository checkout

## 1. Validate Server Baseline

From repo root:

```bash
bash scripts/run-uhome-server-checks.sh
source ~/.udos/venv/uhome-server/bin/activate
```

One-command local console launch:

```bash
bash scripts/first-run-launch.sh
```

## 2. Start Runtime

```bash
python -m uvicorn uhome_server.app:app --host 127.0.0.1 --port 8000 --reload
```

## 3. Validate Runtime Health

```bash
curl http://127.0.0.1:8000/api/health
curl http://127.0.0.1:8000/api/runtime/ready
curl http://127.0.0.1:8000/api/runtime/info
```

## 4. Validate Console Surface

```bash
curl http://127.0.0.1:8000/api/runtime/thin/automation
curl http://127.0.0.1:8000/api/launcher/menu
```

## 5. Validate CLI Console Lane

```bash
source ~/.udos/venv/uhome-server/bin/activate
uhome launcher status
uhome contracts sync-record
```

## Optional Shell Handoff

If shell is present as a sibling repo, launch shell and route to server-facing runtime checks after bringing server up.

```bash
cd ../uDOS-shell
npm run go:run
```

## Expected Result

- uHOME runtime starts cleanly
- health and runtime endpoints return ready status
- thin automation/console status surface is reachable
- CLI console commands return launcher/runtime state
