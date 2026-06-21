#!/bin/bash

# uDosGo Ecosystem - Commit and Push All Repositories
# Version: 1.0
# Purpose: Commit and push all git repositories in the ecosystem

set -e

echo "=========================================="
echo "uDosGo Ecosystem - Commit and Push All"
echo "=========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to commit and push a repository
commit_and_push() {
    local repo_path="$1"
    local repo_name="$2"
    
    echo "Processing: $repo_name"
    echo "----------------------------------------"
    
    # Expand ~ to full path
    if [[ "$repo_path" == ~* ]]; then
        repo_path="${repo_path/#~/$HOME}"
    fi
    
    if [ -d "$repo_path/.git" ]; then
        cd "$repo_path"
        
        # Check current branch
        local branch=$(git branch --show-current 2>/dev/null || echo "unknown")
        echo "Current branch: $branch"
        
        # Check for changes
        if [ -n "$(git status --porcelain)" ]; then
            echo "Changes detected, committing..."
            
            # Add all changes
            git add .
            
            # Commit with a standard message
            git commit -m "Update: $(date +'%Y-%m-%d %H:%M:%S')"
            
            # Push to remote
            if git push origin "$branch" 2>/dev/null; then
                echo -e "${GREEN}✓${NC} $repo_name: Committed and pushed successfully"
            else
                echo -e "${YELLOW}?${NC} $repo_name: Commit successful, but push failed"
            fi
        else
            echo -e "${YELLOW}?${NC} $repo_name: No changes to commit"
        fi
        
        cd - >/dev/null
    else
        echo -e "${RED}✗${NC} $repo_name: Not a git repository"
    fi
    
    echo ""
}

# Main repositories
echo "Processing Main Repositories..."
echo "=========================================="
commit_and_push "~/uDosGo/Home" "Home"
commit_and_push "~/uDosGo/3dWorld" "3dWorld"
commit_and_push "~/uDosGo/Connect" "Connect"
commit_and_push "~/Code" "Code"
commit_and_push "~/Vault" "Vault"

# AgentDigitalOK repositories
echo "Processing AgentDigitalOK Repositories..."
echo "=========================================="
commit_and_push "~/Code/Vendor/AgentDigitalOK/Hivemind" "Hivemind"

# Applications
echo "Processing Applications..."
echo "=========================================="
commit_and_push "~/Code/Apps/Marksmith" "Marksmith"
commit_and_push "~/Code/Apps/McSnackbar" "McSnackbar"

# Other vendor repositories
echo "Processing Other Vendor Repositories..."
echo "=========================================="
commit_and_push "~/Code/Vendor/airpaint" "airpaint"
commit_and_push "~/Code/Vendor/edit.tf" "edit.tf"
commit_and_push "~/Code/Vendor/markdownify-mcp" "markdownify-mcp"
commit_and_push "~/Code/Vendor/masquerain" "masquerain"
commit_and_push "~/Code/Vendor/milkdown" "milkdown"
commit_and_push "~/Code/Vendor/nextchat" "nextchat"

echo "=========================================="
echo "Commit and Push Complete"
echo "=========================================="
