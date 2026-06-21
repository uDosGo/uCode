#!/usr/bin/env bash

set -eu

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

require_file() {
  if [ ! -f "$1" ]; then
    echo "missing required file: $1" >&2
    exit 1
  fi
}

cd "$REPO_ROOT"

require_file "$REPO_ROOT/README.md"
require_file "$REPO_ROOT/docs/architecture.md"
require_file "$REPO_ROOT/docs/boundary.md"
require_file "$REPO_ROOT/docs/activation.md"
require_file "$REPO_ROOT/docs/getting-started.md"
require_file "$REPO_ROOT/docs/examples.md"
require_file "$REPO_ROOT/docs/server-runtime-handoff.md"
require_file "$REPO_ROOT/docs/release-policy.md"
require_file "$REPO_ROOT/src/README.md"
require_file "$REPO_ROOT/src/matter-bridge-contract.json"
require_file "$REPO_ROOT/src/matter-clone-catalog.json"
require_file "$REPO_ROOT/src/home-assistant-bridge-definition.json"
require_file "$REPO_ROOT/scripts/README.md"
require_file "$REPO_ROOT/tests/README.md"
require_file "$REPO_ROOT/config/README.md"
require_file "$REPO_ROOT/config/bridge-targets.example.json"
require_file "$REPO_ROOT/examples/README.md"
require_file "$REPO_ROOT/examples/basic-matter-bridge.json"
require_file "$REPO_ROOT/examples/basic-home-assistant-clone.json"
require_file "$REPO_ROOT/CHANGELOG.md"

python3 - <<'PY'
import json
from pathlib import Path

repo_root = Path(".").resolve()
source = json.loads((repo_root / "src" / "matter-bridge-contract.json").read_text(encoding="utf-8"))
catalog = json.loads((repo_root / "src" / "matter-clone-catalog.json").read_text(encoding="utf-8"))
bridge_definition = json.loads((repo_root / "src" / "home-assistant-bridge-definition.json").read_text(encoding="utf-8"))
example = json.loads((repo_root / "examples" / "basic-matter-bridge.json").read_text(encoding="utf-8"))
clone_example = json.loads((repo_root / "examples" / "basic-home-assistant-clone.json").read_text(encoding="utf-8"))
targets = json.loads((repo_root / "config" / "bridge-targets.example.json").read_text(encoding="utf-8"))

required = {"extension", "transport", "runtime_owner", "targets", "capabilities"}
for name, payload in {
    "src/matter-bridge-contract.json": source,
    "examples/basic-matter-bridge.json": example,
    "examples/basic-home-assistant-clone.json": clone_example,
}.items():
    missing = sorted(required - payload.keys())
    if missing:
        raise SystemExit(f"{name} missing required fields: {missing}")
    if not isinstance(payload["targets"], list) or not all(isinstance(item, str) for item in payload["targets"]):
        raise SystemExit(f"{name} targets must be a list of strings")
    if not isinstance(payload["capabilities"], list) or not all(isinstance(item, str) for item in payload["capabilities"]):
        raise SystemExit(f"{name} capabilities must be a list of strings")

if catalog.get("extension") != "uHOME-matter":
    raise SystemExit("src/matter-clone-catalog.json extension must be uHOME-matter")

clones = catalog.get("clones")
if not isinstance(clones, list) or not clones:
    raise SystemExit("src/matter-clone-catalog.json clones must be a non-empty list")

for item in clones:
    if not isinstance(item, dict):
        raise SystemExit("each clone definition must be an object")
    missing = {"id", "adapter", "runtime_owner"} - item.keys()
    if missing:
        raise SystemExit(
            "each clone definition must include id, adapter, and runtime_owner"
        )

bridge_targets = targets.get("targets")
if not isinstance(bridge_targets, list) or not bridge_targets:
    raise SystemExit("config/bridge-targets.example.json targets must be a non-empty list")

if bridge_definition.get("runtime_owner") != "uHOME-server":
    raise SystemExit("src/home-assistant-bridge-definition.json runtime_owner must be uHOME-server")

if not isinstance(bridge_definition.get("command_allowlist"), list) or not bridge_definition["command_allowlist"]:
    raise SystemExit("src/home-assistant-bridge-definition.json command_allowlist must be a non-empty list")

if not isinstance(bridge_definition.get("entities"), list) or not bridge_definition["entities"]:
    raise SystemExit("src/home-assistant-bridge-definition.json entities must be a non-empty list")
PY

if command -v rg >/dev/null 2>&1; then
  if rg -n '/Users/fredbook/Code|~/Users/fredbook/Code' \
    "$REPO_ROOT/README.md" \
    "$REPO_ROOT/docs" \
    "$REPO_ROOT/src" \
    "$REPO_ROOT/tests" \
    "$REPO_ROOT/examples" \
    "$REPO_ROOT/config"; then
    echo "private local-root reference found in uHOME-matter" >&2
    exit 1
  fi
else
  if grep -R -nE '/Users/fredbook/Code|~/Users/fredbook/Code' \
    "$REPO_ROOT/README.md" \
    "$REPO_ROOT/docs" \
    "$REPO_ROOT/src" \
    "$REPO_ROOT/tests" \
    "$REPO_ROOT/examples" \
    "$REPO_ROOT/config" >/dev/null 2>&1; then
    echo "private local-root reference found in uHOME-matter" >&2
    exit 1
  fi
fi

echo "uHOME-matter checks passed"
