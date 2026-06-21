#!/bin/bash

# uDosGo Ecosystem Health Check Script
# Version: 1.0
# Purpose: Verify ecosystem structure and repository health

set -e

echo "=========================================="
echo "uDosGo Ecosystem Health Check"
echo "=========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check directory exists
check_dir() {
    local path="$1"
    # Expand ~ to the full home directory path
    if [[ "$path" == ~* ]]; then
        path="${path/#~/$HOME}"
    fi
    if [ -d "$path" ]; then
        echo -e "${GREEN}✓${NC} $1 exists"
        return 0
    else
        echo -e "${RED}✗${NC} $1 missing"
        return 1
    fi
}

# Function to check git repository
check_git() {
    if [ -d "$1/.git" ]; then
        echo -e "${GREEN}✓${NC} $1 is a git repository"
        return 0
    else
        echo -e "${YELLOW}?${NC} $1 is not a git repository"
        return 1
    fi
}

# Function to get git status
get_git_status() {
    if [ -d "$1/.git" ]; then
        cd "$1"
        local branch=$(git branch --show-current 2>/dev/null || echo "unknown")
        local status=$(git status --porcelain 2>/dev/null | wc -l)
        if [ "$status" -eq 0 ]; then
            echo -e "  Branch: $branch, Status: Clean"
        else
            echo -e "  Branch: $branch, Status: $status changes"
        fi
        cd - >/dev/null
    fi
}

echo "Checking Core System (~uDosGo/)..."
echo "----------------------------------------"
check_dir "~/uDosGo"
check_dir "~/uDosGo/Home"
check_dir "~/uDosGo/3dWorld"
check_dir "~/uDosGo/Connect"
check_dir "~/uDosGo/Memory"
check_dir "~/uDosGo/Users"

echo ""
echo "Checking Code Home (~Code/)..."
echo "----------------------------------------"
check_dir "~/Code"
check_dir "~/Code/Apps"
check_dir "~/Code/Dev"
check_dir "~/Code/Vendor"
check_dir "~/Code/Private"

echo ""
echo "Checking Applications (~Code/Apps/)..."
echo "----------------------------------------"
check_dir "~/Code/Apps/Marksmith"
check_dir "~/Code/Apps/McSnackbar"
check_git "~/Code/Apps/Marksmith"
check_git "~/Code/Apps/McSnackbar"
get_git_status "~/Code/Apps/Marksmith"
get_git_status "~/Code/Apps/McSnackbar"

echo ""
echo "Checking Vendor Repositories (~Code/Vendor/)..."
echo "----------------------------------------"
check_dir "~/Code/Vendor/AgentDigitalOK"
check_dir "~/Code/Vendor/AgentDigitalOK/Hivemind"
check_git "~/Code/Vendor/AgentDigitalOK/Hivemind"
get_git_status "~/Code/Vendor/AgentDigitalOK/Hivemind"

check_dir "~/Code/Vendor/airpaint"
check_git "~/Code/Vendor/airpaint"
get_git_status "~/Code/Vendor/airpaint"

check_dir "~/Code/Vendor/edit.tf"
check_git "~/Code/Vendor/edit.tf"
get_git_status "~/Code/Vendor/edit.tf"

echo ""
echo "Checking User Vault (~Vault/)..."
echo "----------------------------------------"
check_dir "~/Vault"
check_git "~/Vault"
get_git_status "~/Vault"

echo ""
echo "=========================================="
echo "Health Check Complete"
echo "=========================================="
