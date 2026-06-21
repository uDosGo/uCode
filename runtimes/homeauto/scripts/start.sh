#!/usr/bin/env bash
set -euo pipefail

echo "Starting uHomeNest services (placeholder)..."
bash ./server/jellyfin/orchestrate.sh start
python3 ./server/api/main.py
