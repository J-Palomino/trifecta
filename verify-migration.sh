#!/bin/bash

# DaisyChain PostgreSQL Migration Verification Script
# Runs comprehensive checks to verify successful migration

echo "========================================"
echo "DaisyChain Migration Verification"
echo "========================================"
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

PASS_COUNT=0
FAIL_COUNT=0
WARN_COUNT=0

check_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((PASS_COUNT++))
}

check_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((FAIL_COUNT++))
}

check_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
    ((WARN_COUNT++))
}

# Test 1: Check PostgreSQL connection in logs
echo "1. Checking PostgreSQL connection..."
if docker-compose logs meshcentral 2>/dev/null | grep -qi "postgres\|postgresql"; then
    check_pass "PostgreSQL connection found in logs"
else
    check_fail "No PostgreSQL connection messages in logs"
fi

# Test 2: Check if MeshCentral is running
echo "2. Checking if MeshCentral is running..."
if docker-compose ps meshcentral 2>/dev/null | grep -q "Up"; then
    check_pass "MeshCentral container is running"
else
    check_fail "MeshCentral container is not running"
fi

# Test 3: Check if PostgreSQL is running (if using local)
echo "3. Checking PostgreSQL service..."
if docker-compose ps postgres 2>/dev/null | grep -q "Up"; then
    check_pass "Local PostgreSQL container is running"
elif [ -n "$PGHOST" ]; then
    check_pass "Using Railway PostgreSQL: $PGHOST"
else
    check_warn "No PostgreSQL service found (may be using NeDB)"
fi

# Test 4: Check config.json for postgres section
echo "4. Checking config.json..."
if [ -f "meshcentral-data/config.json" ]; then
    if grep -q '"postgres"' meshcentral-data/config.json; then
        check_pass "PostgreSQL configuration found in config.json"
    else
        check_warn "No PostgreSQL section in config.json (may be using NeDB)"
    fi
else
    check_fail "config.json not found"
fi

# Test 5: Check if NeDB files still exist (should be kept as backup)
echo "5. Checking NeDB backup files..."
if [ -f "meshcentral-data/meshcentral.db" ]; then
    DB_SIZE=$(ls -lh meshcentral-data/meshcentral.db | awk '{print $5}')
    check_pass "NeDB backup exists ($DB_SIZE)"
else
    check_warn "NeDB files not found (were they deleted?)"
fi

# Test 6: Check for export JSON
echo "6. Checking export file..."
if [ -f "meshcentral-data/meshcentral.db.json" ]; then
    OBJECT_COUNT=$(grep -o '"type"' meshcentral-data/meshcentral.db.json | wc -l)
    check_pass "Export JSON exists with $OBJECT_COUNT objects"
else
    check_warn "No export JSON found (may have been deleted)"
fi

# Test 7: Test web interface accessibility
echo "7. Testing web interface..."
if command -v curl &> /dev/null; then
    if curl -k -s -o /dev/null -w "%{http_code}" https://localhost 2>/dev/null | grep -q "200\|302\|301"; then
        check_pass "Web interface is accessible"
    else
        check_fail "Web interface not accessible (may still be starting)"
    fi
else
    check_warn "curl not available, skipping web test"
fi

# Test 8: Check for DaisyChain title in config
echo "8. Checking DaisyChain branding..."
if grep -q '"title": "DaisyChain"' meshcentral-data/config.json 2>/dev/null; then
    check_pass "DaisyChain title configured correctly"
else
    check_warn "DaisyChain title not found in config"
fi

# Test 9: Check MeshCentral logs for errors
echo "9. Checking for errors in logs..."
ERROR_COUNT=$(docker-compose logs meshcentral 2>/dev/null | grep -i "error" | grep -v "no error" | wc -l)
if [ "$ERROR_COUNT" -eq 0 ]; then
    check_pass "No errors found in MeshCentral logs"
elif [ "$ERROR_COUNT" -lt 5 ]; then
    check_warn "$ERROR_COUNT error(s) found in logs (review manually)"
else
    check_fail "$ERROR_COUNT errors found in logs (review required)"
fi

# Test 10: Check database stats (if available)
echo "10. Checking database statistics..."
DB_STATS=$(docker-compose exec -T meshcentral node node_modules/meshcentral --dbstats 2>/dev/null)
if echo "$DB_STATS" | grep -qi "database\|objects"; then
    check_pass "Database statistics available"
    echo "$DB_STATS" | head -10
else
    check_warn "Unable to retrieve database statistics"
fi

# Summary
echo ""
echo "========================================"
echo "Verification Summary"
echo "========================================"
echo -e "${GREEN}Passed: $PASS_COUNT${NC}"
echo -e "${YELLOW}Warnings: $WARN_COUNT${NC}"
echo -e "${RED}Failed: $FAIL_COUNT${NC}"
echo ""

if [ "$FAIL_COUNT" -eq 0 ]; then
    echo -e "${GREEN}Migration appears successful!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Login to https://localhost (or your domain)"
    echo "2. Verify user accounts"
    echo "3. Check device list"
    echo "4. Wait for agents to reconnect (2-3 minutes)"
    echo "5. Test remote control features"
    echo ""
    exit 0
elif [ "$FAIL_COUNT" -lt 3 ]; then
    echo -e "${YELLOW}Migration completed with some issues${NC}"
    echo "Review failed checks above and consult POSTGRES_MIGRATION.md"
    echo ""
    exit 1
else
    echo -e "${RED}Migration may have failed${NC}"
    echo "Review errors above and consider rollback"
    echo ""
    echo "To rollback:"
    echo "  docker-compose down"
    echo "  # Remove postgres section from config.json.template"
    echo "  ./generate-config.sh"
    echo "  docker-compose up -d"
    echo ""
    exit 2
fi
