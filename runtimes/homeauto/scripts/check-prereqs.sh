#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SHARED_PYTHON_BIN="${UDOS_SHARED_PYTHON_BIN:-}"
USE_SHARED_RESOURCES="${UDOS_USE_SHARED_RESOURCES:-1}"
VENV_PYTHON="${UDOS_VENV_DIR:-$HOME/.udos/venv/uhome-server}/bin/python"

if [[ "${USE_SHARED_RESOURCES}" == "1" && -z "${SHARED_PYTHON_BIN}" ]]; then
  FAMILY_HELPER="${REPO_ROOT}/../scripts/lib/family-python.sh"
  if [[ -f "${FAMILY_HELPER}" ]]; then
    # shellcheck source=/dev/null
    . "${FAMILY_HELPER}"
    ensure_shared_python
    SHARED_PYTHON_BIN="${UDOS_SHARED_PYTHON_BIN:-}"
  fi
fi

if [[ -n "${SHARED_PYTHON_BIN}" && -x "${SHARED_PYTHON_BIN}" ]]; then
  PYTHON_BIN="${SHARED_PYTHON_BIN}"
elif [[ -x "${VENV_PYTHON}" ]]; then
  PYTHON_BIN="${VENV_PYTHON}"
else
  PYTHON_BIN="${PYTHON:-python3}"
fi

exec "${PYTHON_BIN}" -m uhome_server.cli installer check-prereqs "$@"
