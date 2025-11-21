#!/bin/bash
# Railway Project Audit Script for TreeTee
# Run this script to check your Railway configuration

echo "========================================"
echo "TreeTee Railway Configuration Audit"
echo "========================================"
echo ""

echo "1. RAILWAY AUTHENTICATION"
echo "------------------------"
railway whoami
echo ""

echo "2. CURRENT PROJECT STATUS"
echo "------------------------"
railway status
echo ""

echo "3. REQUIRED ENVIRONMENT VARIABLES FOR POSTGRESQL"
echo "-----------------------------------------------"
echo "The following variables should be set in Railway for PostgreSQL:"
echo "  - PGHOST (PostgreSQL host)"
echo "  - PGPORT (PostgreSQL port, default: 5432)"
echo "  - PGUSER (PostgreSQL username)"
echo "  - PGPASSWORD (PostgreSQL password)"
echo "  - PGDATABASE (PostgreSQL database name)"
echo ""

echo "4. REQUIRED ENVIRONMENT VARIABLES FOR MONGODB (if using)"
echo "-------------------------------------------------------"
echo "If you want to use MongoDB instead, you'll need:"
echo "  - MONGO_URL or MONGODB_URI (MongoDB connection string)"
echo ""

echo "5. MESHCENTRAL CONFIGURATION"
echo "----------------------------"
echo "Additional required variables:"
echo "  - HOSTNAME (your domain)"
echo "  - LETSENCRYPT_EMAIL (for SSL certificates)"
echo "  - MESHCENTRAL_CERT_NAME (usually same as HOSTNAME)"
echo "  - LETSENCRYPT_DOMAIN (usually same as HOSTNAME)"
echo "  - LETSENCRYPT_PRODUCTION (true for production SSL)"
echo ""

echo "6. CURRENT CONFIG TEMPLATE"
echo "-------------------------"
echo "Your config.json.template is configured for: PostgreSQL"
if grep -q "mongodb" meshcentral-data/config.json.template 2>/dev/null; then
    echo "MongoDB configuration: FOUND"
else
    echo "MongoDB configuration: NOT FOUND"
fi
echo ""

echo "========================================"
echo "NEXT STEPS:"
echo "========================================"
echo "1. Go to https://railway.app/dashboard"
echo "2. Select the 'TreeTee' project"
echo "3. Check which services/databases are provisioned"
echo "4. For each database, note the connection variables"
echo "5. Ensure all required environment variables are set in Railway"
echo ""
echo "To view variables for a specific service:"
echo "  railway service           # Select service interactively"
echo "  railway variables         # View all environment variables"
echo ""
