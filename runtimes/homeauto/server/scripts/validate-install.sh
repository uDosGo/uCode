#!/bin/bash

# uHOME Server Post-Install Validation Script
# 
# Checks that uHOME Server installed correctly and is operational
# Run this after following DEPLOYMENT-GUIDE.md
#
# Usage:
#   bash scripts/validate-install.sh
#   # or
#   chmod +x scripts/validate-install.sh
#   ./scripts/validate-install.sh
#
# Exit codes:
#   0 = All checks passed
#   1 = One or more checks failed
#   2 = Configuration issue preventing checks

set -e  # Exit on error

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
PASS=0
FAIL=0
WARN=0

# Helper functions
pass() {
  echo -e "${GREEN}✓ PASS${NC}: $1"
  ((PASS++))
}

fail() {
  echo -e "${RED}✗ FAIL${NC}: $1"
  ((FAIL++))
}

warn() {
  echo -e "${YELLOW}⚠ WARN${NC}: $1"
  ((WARN++))
}

info() {
  echo -e "${YELLOW}ℹ INFO${NC}: $1"
}

# Banner
echo "================================"
echo "uHOME Server Post-Install Validator"
echo "================================"
echo ""

# ============================================================
# Phase 1: System Requirements
# ============================================================
echo "Phase 1: Checking system requirements..."
echo ""

# Python version
if python3 --version > /dev/null 2>&1; then
  PY_VERSION=$(python3 --version | awk '{print $2}')
  PY_MAJOR=$(echo $PY_VERSION | cut -d. -f1)
  PY_MINOR=$(echo $PY_VERSION | cut -d. -f2)
  
  if [[ $PY_MAJOR -ge 3 && $PY_MINOR -ge 9 ]]; then
    pass "Python $PY_VERSION (>= 3.9)"
  else
    fail "Python version $PY_VERSION (requires >= 3.9)"
  fi
else
  fail "Python3 not found or not in PATH"
fi

# systemd
if systemctl --version > /dev/null 2>&1; then
  pass "systemd available"
else
  fail "systemd not found (required for service management)"
fi

# Storage check
info "Checking storage configuration..."
if [ -d /media/library ]; then
  if [ -w /media/library ]; then
    pass "Storage /media/library exists and writable"
  else
    fail "Storage /media/library exists but NOT writable"
  fi
else
  warn "Storage /media/library does NOT exist (media indexing will be empty)"
fi

echo ""

# ============================================================
# Phase 2: uHOME Installation
# ============================================================
echo "Phase 2: Checking uHOME Server installation..."
echo ""

# Check if uhome command exists
if command -v uhome &> /dev/null; then
  pass "uhome command available in PATH"
  
  # Get version
  if uhome --version > /dev/null 2>&1; then
    VERSION=$(uhome --version 2>&1)
    pass "uhome version: $VERSION"
  else
    warn "Could not determine uhome version"
  fi
else
  fail "uhome command NOT found in PATH"
  fail "Installation may not be complete"
fi

# Check runtime python environment (shared lane or local fallback)
if [ -n "${UDOS_SHARED_PYTHON_BIN:-}" ] && [ -x "${UDOS_SHARED_PYTHON_BIN}" ]; then
  pass "Shared Python available at ${UDOS_SHARED_PYTHON_BIN}"
elif [ -x "$HOME/.udos/envs/family-py311/bin/python" ]; then
  pass "Shared Python available at $HOME/.udos/envs/family-py311/bin/python"
elif [ -d "$HOME/.udos/venv/uhome-server" ] && [ -f "$HOME/.udos/venv/uhome-server/bin/activate" ]; then
  pass "Python virtualenv exists at $HOME/.udos/venv/uhome-server"
else
  warn "No explicit Python environment detected (~/.udos/venv/uhome-server absent and shared lane not found)"
fi

echo ""

# ============================================================
# Phase 3: Service Status
# ============================================================
echo "Phase 3: Checking service status..."
echo ""

# Check if service is registered
if systemctl cat uhome-server > /dev/null 2>&1; then
  pass "systemd service uhome-server registered"
  
  # Get service status
  SERVICE_STATUS=$(systemctl is-active uhome-server 2>/dev/null || echo "unknown")
  if [ "$SERVICE_STATUS" = "active" ]; then
    pass "Service status: active (running)"
  elif [ "$SERVICE_STATUS" = "inactive" ]; then
    warn "Service status: inactive (not running) - start with: sudo systemctl start uhome-server"
  else
    warn "Service status: $SERVICE_STATUS"
  fi
  
  # Get service enabled status
  ENABLED=$(systemctl is-enabled uhome-server 2>/dev/null || echo "unknown")
  if [ "$ENABLED" = "enabled" ]; then
    pass "Service enabled for auto-start"
  elif [ "$ENABLED" = "disabled" ]; then
    info "Service NOT enabled for auto-start - enable with: sudo systemctl enable uhome-server"
  fi
else
  fail "systemd service uhome-server NOT registered"
  fail "Install service with: sudo tee /etc/systemd/system/uhome-server.service"
fi

echo ""

# ============================================================
# Phase 4: Port and Network
# ============================================================
echo "Phase 4: Checking network configuration..."
echo ""

PORT=7890
API_URL="http://localhost:$PORT/api/health"

if netstat -tulpn 2>/dev/null | grep -q ":$PORT "; then
  pass "Port $PORT is in use by a process"
  
  # Get process name
  PROC=$(lsof -i :$PORT 2>/dev/null | tail -1 | awk '{print $1}')
  info "  Process: $PROC"
else
  warn "Port $PORT is not in use - is service running?"
fi

echo ""

# ============================================================
# Phase 5: API Endpoints
# ============================================================
echo "Phase 5: Testing API endpoints..."
echo ""

# Wait a moment for service to respond if just starting
sleep 1

# Health endpoint
if curl -s -f "$API_URL" > /dev/null 2>&1; then
  HEALTH=$(curl -s "$API_URL" | jq -r '.status // "unknown"')
  if [ "$HEALTH" = "ok" ] || [ "$HEALTH" = "healthy" ]; then
    pass "Health endpoint ($API_URL) responding with status=$HEALTH"
  else
    warn "Health endpoint responding with status=$HEALTH (should be 'ok' or 'healthy')"
  fi
else
  fail "Health endpoint NOT responding - service may not be running"
fi

# Registries endpoint
REGISTRIES_URL="http://localhost:$PORT/api/debug/registries"
if curl -s -f "$REGISTRIES_URL" > /dev/null 2>&1; then
  NODE_COUNT=$(curl -s "$REGISTRIES_URL" | jq '.node_registry | length' 2>/dev/null || echo "?")
  STORAGE_COUNT=$(curl -s "$REGISTRIES_URL" | jq '.storage_registry | length' 2>/dev/null || echo "?")
  pass "Registries endpoint responding with $NODE_COUNT nodes, $STORAGE_COUNT storage members"
else
  warn "Registries endpoint NOT responding"
fi

# Household browse endpoint
BROWSE_URL="http://localhost:$PORT/api/household/browse?q=test&limit=1"
if curl -s -f "$BROWSE_URL" > /dev/null 2>&1; then
  RESULTS=$(curl -s "$BROWSE_URL" | jq '.browse_results | length' 2>/dev/null || echo "?")
  pass "Browse endpoint responding with $RESULTS results"
else
  warn "Browse endpoint NOT responding"
fi

echo ""

# ============================================================
# Phase 6: Workspace and Configuration
# ============================================================
echo "Phase 6: Checking workspace and configuration..."
echo ""

WORKSPACE="$HOME/.workspace"
if [ -d "$WORKSPACE" ]; then
  pass "Workspace directory exists at $WORKSPACE"
  
  # Check registries
  for reg in node-registry.json storage-registry.json; do
    if [ -f "$WORKSPACE/$reg" ]; then
      if python3 -m json.tool "$WORKSPACE/$reg" > /dev/null 2>&1; then
        pass "Registry $reg exists and valid JSON"
      else
        fail "Registry $reg exists but INVALID JSON"
      fi
    else
      warn "Registry $reg does NOT exist"
    fi
  done
else
  fail "Workspace directory NOT found at $WORKSPACE"
fi

echo ""

# ============================================================
# Phase 7: Logs and Diagnostics
# ============================================================
echo "Phase 7: Checking logs for errors..."
echo ""

if command -v journalctl &> /dev/null; then
  ERROR_COUNT=$(journalctl -u uhome-server 2>/dev/null | grep -i "error\|exception\|critical" | wc -l || echo "0")
  
  if [ "$ERROR_COUNT" -eq 0 ]; then
    pass "No errors in journalctl logs"
  else
    warn "Found $ERROR_COUNT error/exception entries in logs"
    info "  View logs with: journalctl -u uhome-server -n 20"
  fi
  
  # Check startup message
  if journalctl -u uhome-server 2>/dev/null | grep -q "Starting.*uHOME\|Service startup complete"; then
    pass "Service startup message found in logs"
  else
    warn "Service startup message not found in logs (service may not have started yet)"
  fi
else
  info "journalctl not available (systemd logging unavailable)"
fi

echo ""

# ============================================================
# Phase 8: Performance and Resource Usage
# ============================================================
echo "Phase 8: Checking resource usage..."
echo ""

# Memory usage
if command -v free &> /dev/null; then
  TOTAL_MEM=$(free -h | grep "Mem:" | awk '{print $2}')
  pass "Available system memory: $TOTAL_MEM"
  
  # Check for uhome process
  if pgrep -f "uhome" > /dev/null 2>&1; then
    PROC_MEM=$(ps aux | grep -i "[u]home.*7890" | awk '{print $6}' | head -1)
    if [ -n "$PROC_MEM" ]; then
      info "  uHOME process memory usage: ~${PROC_MEM}KB"
    fi
  fi
fi

# Disk space
if command -v df &> /dev/null; then
  ROOT_SPACE=$(df -h / | tail -1 | awk '{print $4}')
  pass "Available disk space (root): $ROOT_SPACE"
  
  if [ -d /media/library ]; then
    MEDIA_SPACE=$(df -h /media/library 2>/dev/null | tail -1 | awk '{print $4}' || echo "?")
    pass "Available disk space (library): $MEDIA_SPACE"
  fi
fi

echo ""

# ============================================================
# Phase 9: Optional Components
# ============================================================
echo "Phase 9: Checking optional integrations..."
echo ""

# Home Assistant
if curl -s -f "http://localhost:8123/api/" > /dev/null 2>&1; then
  pass "Home Assistant bridge available (http://localhost:8123)"
else
  info "Home Assistant not detected (optional integration)"
fi

# Jellyfin
if curl -s -f "http://localhost:8096/System/Info" > /dev/null 2>&1; then
  pass "Jellyfin media server available (http://localhost:8096)"
else
  info "Jellyfin not detected (optional integration)"
fi

echo ""

# ============================================================
# Summary
# ============================================================
echo "================================"
echo "Validation Summary"
echo "================================"
echo -e "${GREEN}PASS: $PASS${NC}"
echo -e "${RED}FAIL: $FAIL${NC}"
echo -e "${YELLOW}WARN: $WARN${NC}"
echo ""

if [ $FAIL -eq 0 ]; then
  echo -e "${GREEN}✓ All critical checks passed!${NC}"
  echo ""
  echo "Next steps:"
  echo "  1. Add test media to /media/library"
  echo "  2. Trigger library scan: curl -X POST http://localhost:7890/api/debug/library-rebuild"
  echo "  3. Connect client app and browse media"
  echo "  4. Configure Home Assistant/Jellyfin integrations (if desired)"
  echo ""
  exit 0
else
  echo -e "${RED}✗ Some checks failed - review errors above${NC}"
  echo ""
  echo "Troubleshooting:"
  echo "  - Check service status: systemctl status uhome-server"
  echo "  - View logs: sudo journalctl -u uhome-server -n 50"
  echo "  - Test port:  netstat -tulpn | grep 7890"
  echo "  - Test API: curl http://localhost:7890/api/health"
  echo ""
  exit 1
fi
