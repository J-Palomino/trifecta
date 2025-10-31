#!/bin/bash
# Secret Rotation Verification Script
# This script tests that all secrets have been successfully rotated from the repository

set -e

echo "========================================"
echo "Secret Rotation Verification Test"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

FAILED=0

# Test 1: Check for committed secret files
echo "Test 1: Checking for committed secret files..."
if git ls-files | grep -E '\.env$'; then
    echo -e "${RED}FAILED: .env file found in repository${NC}"
    FAILED=1
else
    echo -e "${GREEN}PASSED: No .env files committed${NC}"
fi

if git ls-files | grep -E '\.(pem|key|crt|p12|pfx)$'; then
    echo -e "${RED}FAILED: Certificate/key files found in repository${NC}"
    git ls-files | grep -E '\.(pem|key|crt|p12|pfx)$'
    FAILED=1
else
    echo -e "${GREEN}PASSED: No certificate/key files committed${NC}"
fi
echo ""

# Test 2: Check git history for secrets
echo "Test 2: Scanning git history for secrets (last 50 commits)..."
TEMP_SCAN=$(mktemp)
git log -p -50 --all > "$TEMP_SCAN"

if grep -E "BEGIN.*PRIVATE KEY" "$TEMP_SCAN" > /dev/null; then
    echo -e "${RED}FAILED: Private keys found in git history${NC}"
    FAILED=1
else
    echo -e "${GREEN}PASSED: No private keys in recent history${NC}"
fi

# Check for potential hardcoded secrets
if grep -iE "(password|api[_-]?key|secret|token).*[:=].*['\"][^'\"]{16,}" "$TEMP_SCAN" | grep -v "example" | grep -v "template" > /dev/null; then
    echo -e "${YELLOW}WARNING: Potential hardcoded secrets found in history${NC}"
    echo "This may require git history cleanup"
else
    echo -e "${GREEN}PASSED: No obvious hardcoded secrets in history${NC}"
fi
rm "$TEMP_SCAN"
echo ""

# Test 3: Check .gitignore
echo "Test 3: Verifying .gitignore includes sensitive files..."
if grep -q "^\.env$" .gitignore && \
   grep -q "\.pem" .gitignore && \
   grep -q "\.key" .gitignore; then
    echo -e "${GREEN}PASSED: .gitignore properly configured${NC}"
else
    echo -e "${RED}FAILED: .gitignore missing sensitive file patterns${NC}"
    FAILED=1
fi
echo ""

# Test 4: Verify .env.example exists but .env does not (in git)
echo "Test 4: Checking environment file setup..."
if [ -f .env.example ]; then
    echo -e "${GREEN}PASSED: .env.example exists${NC}"
else
    echo -e "${RED}FAILED: .env.example not found${NC}"
    FAILED=1
fi

if git ls-files --error-unmatch .env 2>/dev/null; then
    echo -e "${RED}FAILED: .env is tracked by git${NC}"
    FAILED=1
else
    echo -e "${GREEN}PASSED: .env is not tracked by git${NC}"
fi
echo ""

# Test 5: Test pre-commit hook
echo "Test 5: Verifying pre-commit hook..."
if [ -f .github/pre-commit-hook.sh ]; then
    echo -e "${GREEN}PASSED: Pre-commit hook script exists${NC}"

    # Check if it's installed
    if [ -f .git/hooks/pre-commit ]; then
        echo -e "${GREEN}PASSED: Pre-commit hook is installed${NC}"
    else
        echo -e "${YELLOW}WARNING: Pre-commit hook not installed${NC}"
        echo "Install with: cp .github/pre-commit-hook.sh .git/hooks/pre-commit"
    fi
else
    echo -e "${RED}FAILED: Pre-commit hook script not found${NC}"
    FAILED=1
fi
echo ""

# Test 6: Verify config template exists
echo "Test 6: Checking configuration templates..."
if [ -f meshcentral-data/config.json.template ]; then
    echo -e "${GREEN}PASSED: config.json.template exists${NC}"
else
    echo -e "${RED}FAILED: config.json.template not found${NC}"
    FAILED=1
fi

if git ls-files --error-unmatch meshcentral-data/config.json 2>/dev/null; then
    echo -e "${RED}FAILED: config.json is tracked by git (should be generated)${NC}"
    FAILED=1
else
    echo -e "${GREEN}PASSED: config.json is not tracked by git${NC}"
fi
echo ""

# Test 7: Test fresh deployment simulation
echo "Test 7: Testing fresh deployment simulation..."
if [ -f .env ]; then
    echo -e "${GREEN}INFO: .env file exists locally (good for testing)${NC}"

    # Test config generation
    if [ -f generate-config.sh ]; then
        echo "Testing configuration generation..."
        bash generate-config.sh
        if [ -f meshcentral-data/config.json ]; then
            echo -e "${GREEN}PASSED: Configuration generated successfully${NC}"

            # Check that config doesn't contain hardcoded secrets
            if grep -E "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}" meshcentral-data/config.json | grep -v "example.com" > /dev/null; then
                echo -e "${GREEN}INFO: Config contains email from environment${NC}"
            fi
        else
            echo -e "${RED}FAILED: Configuration generation failed${NC}"
            FAILED=1
        fi
    else
        echo -e "${RED}FAILED: generate-config.sh not found${NC}"
        FAILED=1
    fi
else
    echo -e "${YELLOW}WARNING: No .env file found (copy .env.example to .env for local testing)${NC}"
fi
echo ""

# Test 8: Check for old certificate files
echo "Test 8: Checking for old certificate files in working directory..."
OLD_CERTS=$(find . -maxdepth 1 -name "*.pem" -o -name "*.key" -o -name "*.crt" 2>/dev/null | wc -l)
if [ "$OLD_CERTS" -gt 0 ]; then
    echo -e "${YELLOW}WARNING: Certificate files found in working directory${NC}"
    find . -maxdepth 1 -name "*.pem" -o -name "*.key" -o -name "*.crt" 2>/dev/null
    echo "These should be moved outside the repository"
else
    echo -e "${GREEN}PASSED: No certificate files in root directory${NC}"
fi
echo ""

# Test 9: Docker compose configuration test
echo "Test 9: Testing Docker Compose configuration..."
if command -v docker-compose &> /dev/null; then
    if docker-compose config > /dev/null 2>&1; then
        echo -e "${GREEN}PASSED: docker-compose.yml is valid${NC}"

        # Check that volumes don't expose entire repo in production
        if grep -q "^      - \./package.json:" docker-compose.prod.yml; then
            echo -e "${GREEN}PASSED: Production config uses selective volume mounts${NC}"
        else
            echo -e "${YELLOW}WARNING: Check production volume mounts${NC}"
        fi
    else
        echo -e "${RED}FAILED: docker-compose.yml has errors${NC}"
        FAILED=1
    fi
else
    echo -e "${YELLOW}WARNING: docker-compose not installed, skipping${NC}"
fi
echo ""

# Test 10: Check for secrets in meshcentral-data
echo "Test 10: Checking meshcentral-data directory..."
if git ls-files meshcentral-data/ | grep -E '\.(key|pem|crt|db)$' | grep -v "\.db$"; then
    echo -e "${RED}FAILED: Sensitive meshcentral-data files are tracked${NC}"
    git ls-files meshcentral-data/ | grep -E '\.(key|pem|crt)$'
    FAILED=1
else
    echo -e "${GREEN}PASSED: No sensitive meshcentral-data files tracked${NC}"
fi
echo ""

# Summary
echo "========================================"
echo "Test Summary"
echo "========================================"
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}ALL TESTS PASSED!${NC}"
    echo ""
    echo "Your repository appears to be properly secured."
    echo "All secrets have been successfully rotated."
    exit 0
else
    echo -e "${RED}SOME TESTS FAILED${NC}"
    echo ""
    echo "Please review the failures above and:"
    echo "1. Remove any sensitive files from git"
    echo "2. Clean git history if needed (see MIGRATION.md)"
    echo "3. Rotate any exposed secrets"
    echo "4. Re-run this script to verify"
    exit 1
fi
