#!/usr/bin/env bash
set -euo pipefail

bash ./media-vault/validate.sh ./media-vault/example >/dev/null
echo "media vault validate test passed"
