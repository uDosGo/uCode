# First-Time Install Instructions

Use this guide when setting up `uHOME-server` on a clean machine for the first time.

## Target

- macOS or Linux workstation (developer install)
- Ubuntu 20.04+ (operator install)

## 1. Install System Prerequisites

macOS (Homebrew):

```bash
brew install python git
```

Ubuntu/Debian:

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip git
```

## 2. Clone The Repository

```bash
git clone https://github.com/fredporter/uHOME-server.git
cd uHOME-server
```

## 3. Create Virtual Environment And Install

```bash
python3 -m venv ~/.udos/venv/uhome-server
source ~/.udos/venv/uhome-server/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e '.[dev]'
```

## 4. Verify Installation

```bash
source ~/.udos/venv/uhome-server/bin/activate
python -m pytest tests/
```

## 5. Start The Server

```bash
source ~/.udos/venv/uhome-server/bin/activate
python -m uvicorn uhome_server.app:app --host 0.0.0.0 --port 8000
```

Or use the direct console/kiosk launcher:

```bash
bash scripts/first-run-launch.sh
```

macOS wrapper:

```bash
open ./scripts/first-run-launch.command
```

## 6. Validate Endpoints

In another terminal:

```bash
curl http://localhost:8000/api/health
curl http://localhost:8000/api/runtime/ready
curl http://localhost:8000/api/debug/registries
```

## 7. Optional: Use CLI Tools

```bash
source ~/.udos/venv/uhome-server/bin/activate
uhome launcher status
uhome backup create
uhome backup list
```

## 8. Production-Oriented Setup

For full Ubuntu deployment with service management and operations:

- `docs/DEPLOYMENT-GUIDE.md`
- `docs/operations/README.md`
- `scripts/validate-install.sh`

## Common Issues

- `ModuleNotFoundError`: ensure virtualenv is active and reinstall with `pip install -e '.[dev]'`
- Port already in use: run `lsof -i :8000` and stop the conflicting process
- Import errors in tests: run tests from repo root (`uHOME-server/`)
