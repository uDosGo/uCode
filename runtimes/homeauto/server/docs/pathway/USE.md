# Use uHOME Server

Use this path if you want to run or operate **uHomeNest** (**v3.9.x**) — the monorepo that hosts the uHOME server runtime.

## What You Get

- the standalone Linux server runtime
- base runtime support for local automation bridges
- presentation start, stop, and status control
- runtime, dashboard, network, library, and container APIs
- installer bundle verification, staging, promotion, and health checks

## First Steps

1. Create a local virtualenv and install the package in editable mode.
2. Start the API with Python 3.9+ and uvicorn.
3. Use the CLI entrypoints for launcher or installer flows.

```bash
python3 -m venv ~/.udos/venv/uhome-server
~/.udos/venv/uhome-server/bin/python -m pip install --upgrade pip setuptools wheel
~/.udos/venv/uhome-server/bin/python -m pip install -e '.[dev]'
~/.udos/venv/uhome-server/bin/python -m uvicorn uhome_server.app:app --reload
```

## Primary Runtime Surfaces

- `src/uhome_server/app.py`
- `src/uhome_server/cli.py`
- `src/uhome_server/routes/`
- `src/uhome_server/services/`

## Operational Docs

- `docs/howto/SONIC-STANDALONE-RELEASE-AND-INSTALL.md`
- `docs/ui/UHOME-DASHBOARD.md`
- `docs/STATUS.md`

## Important Boundary Rule

This repo owns the home-infrastructure runtime. It does not own generic
deployment bootstrap as a product category. When install logic becomes generic
or hardware-first, it should move toward `sonic-screwdriver`.

Matter, Home Assistant, and local automation contracts should move through
`uHOME-matter`. Remote webhook-style and host-local operator jobs are not owned
by the uHOME stream; see `uDOS-wizard` and `uDOS-ubuntu` documentation.
