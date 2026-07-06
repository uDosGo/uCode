#!/usr/bin/env bash
# One-line uCode BASIC runtime installer.
# Usage: curl -fsSL https://.../install.sh | bash
set -euo pipefail

UCODE_ROOT="${UCODE_ROOT:-$HOME/.ucode}"
RUNTIME_DIR="$UCODE_ROOT/runtimes/basic"
VENV_DIR="$RUNTIME_DIR/.venv"

echo "uCode BASIC runtime installer"
echo "-----------------------------"

# Ensure Python 3.12+
if ! command -v python3 &>/dev/null; then
  echo "ERROR: python3 is required. Install it first (brew install python@3.12)."
  exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "  Python $PYTHON_VERSION detected"

mkdir -p "$RUNTIME_DIR"

# Create venv if not present
if [ ! -d "$VENV_DIR" ]; then
  echo "  Creating virtual environment..."
  python3 -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

# Install runtime package in editable mode
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
pip install -e "$SCRIPT_DIR" --quiet

# Create ucode CLI wrapper
cat > "$UCODE_ROOT/bin/ucode-basic" << 'WRAPPER'
#!/usr/bin/env bash
source "$HOME/.ucode/runtimes/basic/.venv/bin/activate"
exec python -m ucode1 "$@"
WRAPPER
chmod +x "$UCODE_ROOT/bin/ucode-basic"

# Symlink to /usr/local/bin if writable
if [ -w /usr/local/bin ] || [ -w /opt/homebrew/bin ]; then
  TARGET_DIR="${HOMEBREW_PREFIX:-/usr/local}/bin"
  ln -sf "$UCODE_ROOT/bin/ucode-basic" "$TARGET_DIR/ucode" 2>/dev/null || true
  echo "  Linked: $TARGET_DIR/ucode -> ucode-basic"
fi

echo ""
echo "Installation complete."
echo "Run: ucode --help"