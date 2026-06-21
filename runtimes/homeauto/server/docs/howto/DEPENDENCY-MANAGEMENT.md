# Dependency Management

Status: canonical
Updated: 2026-03-10

## Overview

**uHomeNest** uses `pyproject.toml` for dependency declarations and
`requirements.lock` for reproducible builds.

## Lockfile Policy

- `requirements.lock` pins exact versions for CI and production deployments
- generated from a clean virtual environment with `pip freeze`
- updated when dependencies are added, removed, or intentionally upgraded

## Updating the Lockfile

When updating dependencies:

```bash
# 1. Clean install from pyproject.toml
python -m venv ~/.udos/venv/uhome-server
source ~/.udos/venv/uhome-server/bin/activate
pip install -e '.[dev]'

# 2. Generate lockfile
pip freeze > requirements.lock

# 3. Verify tests still pass
pytest tests/
```

CI will install from `requirements.lock` to ensure reproducible builds.

## Local Development

For local development, either:

- install from lockfile: `pip install -r requirements.lock`
- install from pyproject.toml: `pip install -e '.[dev]'`

The lockfile ensures CI matches production; pyproject.toml allows flexible local
iteration.
