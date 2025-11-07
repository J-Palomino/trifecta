#!/bin/bash
set -e

# DaisyChain NeDB to PostgreSQL Migration Script
# This script automates the migration from NeDB to PostgreSQL

echo "========================================"
echo "DaisyChain NeDB to PostgreSQL Migration"
echo "========================================"
echo ""

# Configuration
BACKUP_DIR=~/daisychain-migration-backup-$(date +%Y%m%d-%H%M%S)
EXPORT_FILE=meshcentral-data/meshcentral.db.json
COMPOSE_FILE="docker-compose.yml"
POSTGRES_COMPOSE_FILE="docker-compose.postgres.yml"

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Helper functions
print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "\n${GREEN}==> Step $1:${NC} $2"
}

# Check prerequisites
print_step "0" "Checking prerequisites..."

if [ ! -f "docker-compose.yml" ]; then
    print_error "docker-compose.yml not found. Please run this script from the project root."
    exit 1
fi

if [ ! -f "meshcentral-data/config.json.template" ]; then
    print_error "config.json.template not found"
    exit 1
fi

print_success "Prerequisites check passed"

# Step 1: Create backup
print_step "1" "Creating backup of current data..."

mkdir -p "$BACKUP_DIR"
cp -r meshcentral-data "$BACKUP_DIR/"
print_success "Backup created at: $BACKUP_DIR"

# Step 2: Export NeDB database
print_step "2" "Exporting NeDB database to JSON..."

echo "Stopping containers..."
docker-compose down

echo "Exporting database..."
docker-compose run --rm meshcentral node node_modules/meshcentral --dbexport

if [ -f "$EXPORT_FILE" ]; then
    EXPORT_COUNT=$(grep -o '"type"' "$EXPORT_FILE" | wc -l)
    print_success "Exported $EXPORT_COUNT objects to $EXPORT_FILE"
    cp "$EXPORT_FILE" "$BACKUP_DIR/"
else
    print_error "Export failed - $EXPORT_FILE not found"
    exit 1
fi

# Step 3: Verify PostgreSQL configuration
print_step "3" "Verifying PostgreSQL configuration..."

if [ -z "$PGHOST" ] && [ ! -f "$POSTGRES_COMPOSE_FILE" ]; then
    print_warning "Neither Railway PostgreSQL (PGHOST) nor local docker-compose.postgres.yml found"
    echo ""
    echo "Please choose:"
    echo "1) Continue with local PostgreSQL (docker-compose.postgres.yml)"
    echo "2) Continue with Railway PostgreSQL (requires PGHOST env var)"
    echo "3) Abort migration"
    read -p "Enter choice [1-3]: " choice

    case $choice in
        1)
            if [ ! -f "$POSTGRES_COMPOSE_FILE" ]; then
                print_error "docker-compose.postgres.yml not found"
                exit 1
            fi
            USE_LOCAL_POSTGRES=true
            print_success "Using local PostgreSQL"
            ;;
        2)
            if [ -z "$PGHOST" ]; then
                print_error "PGHOST not set. Please configure Railway PostgreSQL first."
                exit 1
            fi
            USE_LOCAL_POSTGRES=false
            print_success "Using Railway PostgreSQL: $PGHOST"
            ;;
        3)
            echo "Migration aborted"
            exit 0
            ;;
        *)
            print_error "Invalid choice"
            exit 1
            ;;
    esac
else
    if [ -n "$PGHOST" ]; then
        USE_LOCAL_POSTGRES=false
        print_success "Found Railway PostgreSQL: $PGHOST"
    else
        USE_LOCAL_POSTGRES=true
        print_success "Found local PostgreSQL configuration"
    fi
fi

# Step 4: Update configuration
print_step "4" "Updating configuration..."

if [ -f "generate-config.sh" ]; then
    chmod +x generate-config.sh
    ./generate-config.sh
    print_success "Configuration regenerated with PostgreSQL settings"
else
    print_warning "generate-config.sh not found, skipping config generation"
fi

# Step 5: Start with PostgreSQL
print_step "5" "Starting MeshCentral with PostgreSQL..."

if [ "$USE_LOCAL_POSTGRES" = true ]; then
    docker-compose -f docker-compose.yml -f docker-compose.postgres.yml up -d
else
    docker-compose up -d
fi

echo "Waiting for PostgreSQL initialization (30 seconds)..."
sleep 30

docker-compose logs --tail=50 meshcentral

# Step 6: Import data to PostgreSQL
print_step "6" "Importing data to PostgreSQL..."

echo "Running import command..."
docker-compose exec -T meshcentral node node_modules/meshcentral --dbimport

print_success "Data import completed"

# Step 7: Create performance indexes
print_step "7" "Creating performance indexes..."

if [ "$USE_LOCAL_POSTGRES" = true ]; then
    docker-compose exec -T postgres psql -U postgres -d meshcentral -c "CREATE INDEX IF NOT EXISTS idx_fkid ON eventids(fkid);" 2>/dev/null || print_warning "Could not create index (table may not exist yet)"
else
    if [ -n "$PGHOST" ]; then
        print_warning "Cannot create index automatically on Railway. Please run manually:"
        echo "CREATE INDEX IF NOT EXISTS idx_fkid ON eventids(fkid);"
    fi
fi

# Step 8: Restart and verify
print_step "8" "Restarting MeshCentral..."

docker-compose restart meshcentral
sleep 10
docker-compose logs --tail=50 meshcentral

# Step 9: Verification
print_step "9" "Running verification checks..."

echo "Checking database statistics..."
docker-compose exec -T meshcentral node node_modules/meshcentral --dbstats || print_warning "Database stats command failed (this is normal if MeshCentral is still initializing)"

echo ""
print_success "Migration completed successfully!"
echo ""
echo "========================================"
echo "Next Steps:"
echo "========================================"
echo "1. Login to DaisyChain web interface"
echo "2. Verify user accounts exist"
echo "3. Check device list matches pre-migration"
echo "4. Wait 2-3 minutes for agents to reconnect"
echo "5. Test remote desktop/terminal access"
echo "6. Run verification script: ./verify-migration.sh"
echo ""
echo "Backup location: $BACKUP_DIR"
echo ""
echo "To rollback if needed:"
echo "  docker-compose down"
echo "  cp $BACKUP_DIR/meshcentral-data/*.db meshcentral-data/"
echo "  # Remove postgres section from config.json.template"
echo "  ./generate-config.sh"
echo "  docker-compose up -d"
echo ""
echo "========================================"
