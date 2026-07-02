#!/bin/bash
# scripts/serve-dist.sh
# Serves the built embeddable bundles for external consumption.

# Ensure we are at the root
cd "$(dirname "$0")/.."

echo "Preparing embeddables..."
mkdir -p dist-embed
cp packages/gridcore/dist/index.global.js dist-embed/gridcore.js
cp packages/viewport-renderer/dist/index.global.js dist-embed/viewport-renderer.js

echo "Serving embeddables at http://localhost:8000"
echo "Files available:"
echo " - http://localhost:8000/gridcore.js"
echo " - http://localhost:8000/viewport-renderer.js"

# Use python3 to serve the directory
python3 -m http.server 8000 --directory dist-embed
