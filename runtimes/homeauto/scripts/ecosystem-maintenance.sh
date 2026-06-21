#!/bin/bash

# uDosGo Ecosystem Maintenance Script
# Version: 1.0
# Purpose: Perform maintenance tasks on the ecosystem

set -e

echo "=========================================="
echo "uDosGo Ecosystem Maintenance"
echo "=========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to update repository
update_repo() {
    local repo_path=$1
    local repo_name=$(basename "$repo_path")
    
    if [ -d "$repo_path/.git" ]; then
        echo -e "${GREEN}Updating $repo_name...${NC}"
        cd "$repo_path"
        git fetch origin 2>/dev/null
        git pull origin main 2>/dev/null
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓${NC} $repo_name updated successfully"
        else
            echo -e "${RED}✗${NC} $repo_name update failed"
        fi
        cd - >/dev/null
    else
        echo -e "${YELLOW}?${NC} $repo_name is not a git repository"
    fi
}

echo "Updating Core System Repositories..."
echo "----------------------------------------"
update_repo "~/uDosGo/Home"
update_repo "~/uDosGo/3dWorld"
update_repo "~/uDosGo/Connect"

echo ""
echo "Updating Code Home Repositories..."
echo "----------------------------------------"
update_repo "~/Code/Apps/Marksmith"
update_repo "~/Code/Apps/McSnackbar"
update_repo "~/Code/Vendor/AgentDigitalOK/Hivemind"
update_repo "~/Code/Vendor/airpaint"
update_repo "~/Code/Vendor/edit.tf"
update_repo "~/Code/Vendor/nextchat"
update_repo "~/Code/Vendor/markdownify-mcp"
update_repo "~/Code/Vendor/masquerain"
update_repo "~/Code/Vendor/milkdown"

echo ""
echo "Updating User Vault..."
echo "----------------------------------------"
update_repo "~/Vault"

echo ""
echo "=========================================="
echo "Maintenance Complete"
echo "=========================================="
