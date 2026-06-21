#!/usr/bin/env bash

set -eu

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SHARED_PYTHON_BIN="${UDOS_SHARED_PYTHON_BIN:-}"
USE_SHARED_RESOURCES="${UDOS_USE_SHARED_RESOURCES:-1}"
VENV_DIR="${UDOS_VENV_DIR:-$HOME/.udos/venv/uhome-server}"
PYTHON_BIN="$VENV_DIR/bin/python"

cd "$REPO_ROOT"
mkdir -p "$VENV_DIR"

if [ "$USE_SHARED_RESOURCES" = "1" ] && [ -z "$SHARED_PYTHON_BIN" ]; then
  FAMILY_HELPER="$REPO_ROOT/../scripts/lib/family-python.sh"
  if [ -f "$FAMILY_HELPER" ]; then
    # shellcheck source=/dev/null
    . "$FAMILY_HELPER"
    ensure_shared_python
    SHARED_PYTHON_BIN="${UDOS_SHARED_PYTHON_BIN:-}"
  fi
fi

if [ -n "$SHARED_PYTHON_BIN" ] && [ -x "$SHARED_PYTHON_BIN" ]; then
  PYTHON_BIN="$SHARED_PYTHON_BIN"
elif [ ! -x "$PYTHON_BIN" ]; then
  python3 -m venv "$VENV_DIR"
  "$PYTHON_BIN" -m pip install --upgrade pip setuptools wheel
  "$PYTHON_BIN" -m pip install -e '.[dev]'
fi

if ! "$PYTHON_BIN" -c 'import uhome_server' >/dev/null 2>&1; then
  "$PYTHON_BIN" -m pip install -e '.[dev]'
fi

"$PYTHON_BIN" -m pytest tests
