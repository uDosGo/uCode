# Basic uHOME-server Session

This is the smallest v2-local walkthrough for validating `uHOME-server` as a
standalone local-service runtime.

## Validate The Repo

```bash
scripts/run-uhome-server-checks.sh
```

## Start The App

```bash
~/.udos/venv/uhome-server/bin/python -m uvicorn uhome_server.app:app --reload
```

## Verify Health

In another terminal:

```bash
curl http://127.0.0.1:8000/api/health
```

Expected outcome:

- the health route responds successfully
- local service development stays inside `uHOME-server`
- shell UX remains in `uDOS-shell`
- provider-backed assist remains in `uDOS-wizard`
