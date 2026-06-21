#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
RUN_DIR="${REPO_ROOT}/.run"
SHARED_PYTHON_BIN="${UDOS_SHARED_PYTHON_BIN:-}"
USE_SHARED_RESOURCES="${UDOS_USE_SHARED_RESOURCES:-1}"
VENV_DIR="${UDOS_VENV_DIR:-$HOME/.udos/venv/uhome-server}"
PYTHON_BIN="${VENV_DIR}/bin/python"
PORT="${UHOME_PORT:-8000}"
HOST="${UHOME_HOST:-127.0.0.1}"
SERVER_PID_FILE="${RUN_DIR}/uhome-server.pid"
SERVER_LOG="${RUN_DIR}/uhome-server.log"
AUTO_START_PRESENTATION="${UHOME_PRESENTATION:-thin-gui}"
CONSOLE_URL="http://${HOST}:${PORT}/api/runtime/thin/automation"
MENU_URL="http://${HOST}:${PORT}/api/launcher/menu"
START_URL="http://${HOST}:${PORT}/api/launcher/start"

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "missing required command: $1" >&2
    exit 1
  fi
}

wait_for_http() {
  local url="$1"
  local attempts="${2:-20}"
  local delay="${3:-1}"
  for ((i=0; i<attempts; i++)); do
    if python3 - <<PY >/dev/null 2>&1
import urllib.request
urllib.request.urlopen("${url}", timeout=1).read()
PY
    then
      return 0
    fi
    sleep "${delay}"
  done
  return 1
}

post_json() {
  local url="$1"
  local payload="$2"
  python3 - <<PY >/dev/null
import json
import urllib.request

request = urllib.request.Request(
    "${url}",
    data=json.dumps(${payload}).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST",
)
urllib.request.urlopen(request, timeout=5).read()
PY
}

open_url() {
  local url="$1"
  if command -v open >/dev/null 2>&1; then
    open "${url}" >/dev/null 2>&1 || true
  elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open "${url}" >/dev/null 2>&1 || true
  fi
}

require_cmd python3
require_cmd bash

mkdir -p "${RUN_DIR}"
mkdir -p "${VENV_DIR}"
cd "${REPO_ROOT}"

echo "Bootstrapping uHOME-server..."
bash "${SCRIPT_DIR}/run-uhome-server-checks.sh" >/dev/null

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
fi

if [[ ! -x "${PYTHON_BIN}" ]]; then
  echo "ERROR Missing python interpreter at ${PYTHON_BIN}" >&2
  exit 1
fi

if [[ -f "${SERVER_PID_FILE}" ]] && kill -0 "$(cat "${SERVER_PID_FILE}" 2>/dev/null)" 2>/dev/null; then
  echo "uHOME-server already running on pid $(cat "${SERVER_PID_FILE}")"
else
  nohup "${PYTHON_BIN}" -m uvicorn uhome_server.app:app --host "${HOST}" --port "${PORT}" >"${SERVER_LOG}" 2>&1 &
  echo $! >"${SERVER_PID_FILE}"
  echo "Started uHOME-server on http://${HOST}:${PORT}"
fi

if ! wait_for_http "http://${HOST}:${PORT}/api/health" 20 1; then
  echo "uHOME-server failed to start on port ${PORT}" >&2
  echo "--- uhome-server log ---" >&2
  cat "${SERVER_LOG}" >&2 || true
  exit 1
fi

post_json "${START_URL}" "{\"presentation\": \"${AUTO_START_PRESENTATION}\"}"

if ! wait_for_http "${MENU_URL}" 10 1; then
  echo "uHOME launcher menu did not become available" >&2
  exit 1
fi

open_url "${CONSOLE_URL}"

echo ""
echo "uHOME console is running."
echo "  Server:  http://${HOST}:${PORT}"
echo "  Console: ${CONSOLE_URL}"
echo "  Menu:    ${MENU_URL}"
echo "  Log:     ${SERVER_LOG}"
echo ""
echo "Default presentation started: ${AUTO_START_PRESENTATION}"
