#!/bin/bash
# Git History Cleanup Script
# This script removes sensitive files from git history
# WARNING: This rewrites git history!

set -e

echo "================================="
echo "Git History Cleanup Script"
echo "================================="
echo ""
echo "WARNING: This will rewrite git history!"
echo "This affects all repository users."
echo ""
read -p "Have you coordinated with your team? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Aborting. Please coordinate with your team first."
    exit 1
fi

echo ""
echo "This script will remove the following from git history:"
echo "  - *.pem files"
echo "  - *.key files"
echo "  - *.crt files"
echo "  - meshcentral-data/config.json"
echo ""
read -p "Continue? (yes/no): " continue_confirm

if [ "$continue_confirm" != "yes" ]; then
    echo "Aborting."
    exit 1
fi

# Create a backup branch
echo ""
echo "Creating backup branch..."
git branch backup-before-cleanup-$(date +%Y%m%d-%H%M%S)

# Method 1: Using git filter-branch (built-in)
echo ""
echo "Cleaning git history using git filter-branch..."

# Remove certificate files
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch *.pem *.key *.crt' \
  --prune-empty --tag-name-filter cat -- --all

# Remove meshcentral config
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch meshcentral-data/config.json' \
  --prune-empty --tag-name-filter cat -- --all

# Remove all private keys from meshcentral-data
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch meshcentral-data/*-private.key' \
  --prune-empty --tag-name-filter cat -- --all

# Remove -old certificate files
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch meshcentral-data/*.key-old meshcentral-data/*.crt-old' \
  --prune-empty --tag-name-filter cat -- --all

# Clean up
echo ""
echo "Cleaning up refs..."
rm -rf .git/refs/original/
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo ""
echo "================================="
echo "Cleanup Complete!"
echo "================================="
echo ""
echo "Next steps:"
echo "1. Review the changes: git log --all --oneline"
echo "2. Test locally: docker-compose up -d"
echo "3. Force push to remote:"
echo "   git push origin --force --all"
echo "   git push origin --force --tags"
echo ""
echo "4. All team members must re-clone:"
echo "   git clone <repo-url> new-folder"
echo ""
echo "5. Rotate all exposed secrets:"
echo "   - Generate new SSL certificates"
echo "   - Update MeshCentral admin password"
echo "   - Regenerate any API tokens"
echo ""
