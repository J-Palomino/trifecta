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

# Generate config.json from template if template exists
if [ -f meshcentral-data/config.json.template ]; then
    echo "Generating config.json from template..."
    envsubst < meshcentral-data/config.json.template > meshcentral-data/config.json
    echo "Configuration generated successfully!"
    echo "Using hostname: $MESHCENTRAL_CERT_NAME"
else
    echo "WARNING: config.json.template not found"
fi

# Start MeshCentral
echo "Starting MeshCentral..."
exec node ./node_modules/meshcentral
