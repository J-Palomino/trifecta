#!/bin/bash
set -e

echo "Generating MeshCentral configuration from environment variables..."

# Set defaults for required variables
export MESHCENTRAL_CERT_NAME=${MESHCENTRAL_CERT_NAME:-${HOSTNAME:-localhost}}
export MESHCENTRAL_PORT=${MESHCENTRAL_PORT:-443}
export MESHCENTRAL_REDIRECT_PORT=${MESHCENTRAL_REDIRECT_PORT:-80}
export ALLOW_LOGIN_TOKEN=${ALLOW_LOGIN_TOKEN:-true}
export WAN_ONLY=${WAN_ONLY:-false}
export ALLOW_NEW_ACCOUNTS=${ALLOW_NEW_ACCOUNTS:-false}
export ENABLE_IPKVM=${ENABLE_IPKVM:-false}
export LETSENCRYPT_EMAIL=${LETSENCRYPT_EMAIL:-admin@example.com}
export LETSENCRYPT_DOMAIN=${LETSENCRYPT_DOMAIN:-${HOSTNAME:-localhost}}
export LETSENCRYPT_PRODUCTION=${LETSENCRYPT_PRODUCTION:-false}

# PostgreSQL configuration (Railway provides these via PGHOST, PGPORT, etc.)
export POSTGRES_HOST=${POSTGRES_HOST:-${PGHOST:-}}
export POSTGRES_PORT=${POSTGRES_PORT:-${PGPORT:-5432}}
export POSTGRES_USER=${POSTGRES_USER:-${PGUSER:-postgres}}
export POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-${PGPASSWORD:-}}
export POSTGRES_DATABASE=${POSTGRES_DATABASE:-${PGDATABASE:-meshcentral}}

# Generate config.json from template if template exists
if [ -f meshcentral-data/config.json.template ]; then
    echo "Generating config.json from template..."
    # Always regenerate config.json to pick up template changes
    echo "Removing old config.json if it exists..."
    rm -f meshcentral-data/config.json
    # Use explicit variable list to avoid substituting $ in bash commands within JSON
    envsubst '$MESHCENTRAL_CERT_NAME $MESHCENTRAL_PORT $MESHCENTRAL_REDIRECT_PORT $ALLOW_LOGIN_TOKEN $WAN_ONLY $ALLOW_NEW_ACCOUNTS $ENABLE_IPKVM $LETSENCRYPT_EMAIL $LETSENCRYPT_DOMAIN $LETSENCRYPT_PRODUCTION $POSTGRES_HOST $POSTGRES_PORT $POSTGRES_USER $POSTGRES_PASSWORD $POSTGRES_DATABASE' \
        < meshcentral-data/config.json.template > meshcentral-data/config.json
    echo "Configuration generated successfully!"
    echo "Using hostname: $MESHCENTRAL_CERT_NAME"
else
    echo "WARNING: config.json.template not found"
fi

# Start MeshCentral
echo "Starting MeshCentral..."
exec node ./node_modules/meshcentral
