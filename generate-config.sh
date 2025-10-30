#!/bin/bash
set -e

echo "Generating MeshCentral configuration from environment variables..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found!"
    echo "Please copy .env.example to .env and configure your settings."
    exit 1
fi

# Load environment variables safely
set -a
source .env
set +a

# Set defaults if not provided
export MESHCENTRAL_CERT_NAME=${MESHCENTRAL_CERT_NAME:-${HOSTNAME}}
export MESHCENTRAL_PORT=${MESHCENTRAL_PORT:-443}
export MESHCENTRAL_REDIRECT_PORT=${MESHCENTRAL_REDIRECT_PORT:-80}
export ALLOW_LOGIN_TOKEN=${ALLOW_LOGIN_TOKEN:-true}
export WAN_ONLY=${WAN_ONLY:-true}
export ALLOW_NEW_ACCOUNTS=${ALLOW_NEW_ACCOUNTS:-false}
export ENABLE_IPKVM=${ENABLE_IPKVM:-false}
export LETSENCRYPT_EMAIL=${LETSENCRYPT_EMAIL}
export LETSENCRYPT_DOMAIN=${LETSENCRYPT_DOMAIN:-${HOSTNAME}}
export LETSENCRYPT_PRODUCTION=${LETSENCRYPT_PRODUCTION:-true}

# Generate config.json from template
if [ -f meshcentral-data/config.json.template ]; then
    echo "Generating meshcentral-data/config.json from template..."
    envsubst < meshcentral-data/config.json.template > meshcentral-data/config.json
    echo "Configuration generated successfully!"
else
    echo "WARNING: config.json.template not found, skipping generation."
fi

# Check if SSL certificates exist
if [ ! -f "${SSL_CERT_PATH}" ] || [ ! -f "${SSL_KEY_PATH}" ]; then
    echo "WARNING: SSL certificate files not found at specified paths:"
    echo "  SSL_CERT_PATH: ${SSL_CERT_PATH}"
    echo "  SSL_KEY_PATH: ${SSL_KEY_PATH}"
    echo ""
    echo "If you're using Let's Encrypt, MeshCentral will generate certificates automatically."
    echo "Otherwise, please ensure your certificate files are in place before starting."
fi

echo ""
echo "Configuration complete! You can now start the application."
