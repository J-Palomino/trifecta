#!/bin/bash
# Git pre-commit hook to prevent committing secrets
# Install this hook with: cp .github/pre-commit-hook.sh .git/hooks/pre-commit

echo "Running pre-commit security checks..."

# Check for .env files
if git diff --cached --name-only | grep -E '\.env$' > /dev/null; then
    echo "❌ ERROR: Attempting to commit .env file!"
    echo "   .env files should never be committed to version control."
    echo "   Add .env to .gitignore"
    exit 1
fi

# Check for certificate and key files
if git diff --cached --name-only | grep -E '\.(pem|key|crt|p12|pfx)$' > /dev/null; then
    echo "❌ ERROR: Attempting to commit certificate or key files!"
    echo "   Certificate and key files should never be committed."
    echo "   Files found:"
    git diff --cached --name-only | grep -E '\.(pem|key|crt|p12|pfx)$'
    echo ""
    echo "   These files should be:"
    echo "   1. Added to .gitignore"
    echo "   2. Stored securely outside the repository"
    echo "   3. Referenced via environment variables"
    exit 1
fi

# Check for MeshCentral private keys
if git diff --cached --name-only | grep -E 'meshcentral-data/.*private\.key' > /dev/null; then
    echo "❌ ERROR: Attempting to commit MeshCentral private keys!"
    echo "   These files should be in .gitignore"
    exit 1
fi

# Check for common secret patterns in staged content (excluding documentation)
TEMP_FILE=$(mktemp)
git diff --cached -- ':!*.md' > "$TEMP_FILE"

# Check for private keys in content (already excluding .md files via TEMP_FILE)
# Pattern split to avoid matching this check itself
KEY_PATTERN="BEGIN.*PRIVATE"" KEY"
if grep -E "$KEY_PATTERN" "$TEMP_FILE" > /dev/null; then
    echo "❌ ERROR: Private key detected in staged changes!"
    echo "   Private keys should never be committed to version control."
    echo "   Note: Documentation examples in .md files are excluded from this check."
    rm "$TEMP_FILE"
    exit 1
fi

# Check for common secret patterns (passwords, api keys, tokens)
if grep -iE "(password|api[_-]?key|secret|token|credential).*[:=].*['\"][^'\"]{8,}" "$TEMP_FILE" | grep -v "example" | grep -v "template" > /dev/null; then
    echo "⚠️  WARNING: Possible hardcoded secret detected in staged changes!"
    echo "   Please review your changes for hardcoded secrets."
    echo "   Secrets should be stored in environment variables."
    echo ""
    echo "   If this is a false positive, you can skip this check with:"
    echo "   git commit --no-verify"
    echo ""
    read -p "Do you want to continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        rm "$TEMP_FILE"
        exit 1
    fi
fi

# Check for email addresses (might be sensitive)
if grep -E "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}" "$TEMP_FILE" | grep -v "example.com" | grep -v "@users.noreply.github.com" > /dev/null; then
    echo "⚠️  WARNING: Email address detected in staged changes!"
    echo "   Consider using environment variables for email addresses."
    echo ""
    echo "   If this is acceptable, you can skip this check with:"
    echo "   git commit --no-verify"
    echo ""
    read -p "Do you want to continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        rm "$TEMP_FILE"
        exit 1
    fi
fi

rm "$TEMP_FILE"

echo "✓ Pre-commit security checks passed!"
exit 0
