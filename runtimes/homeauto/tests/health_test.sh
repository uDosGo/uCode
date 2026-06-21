#!/usr/bin/env bash
set -euo pipefail

curl -fsS http://127.0.0.1:7890/api/health | rg '"status"\s*:\s*"ok"'
echo "health test passed"
