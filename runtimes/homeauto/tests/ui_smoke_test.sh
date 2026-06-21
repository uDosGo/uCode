#!/usr/bin/env bash
set -euo pipefail

test -f ./ui/templates/launcher.html
test -f ./ui/usxd/launcher.json
echo "ui smoke test passed"
