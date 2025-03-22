#!/bin/bash

echo "Starting MeshCentral and redirect handler for cloud deployment..."

# Set default hostname if not provided
export HOSTNAME=${HOSTNAME:-tee.up.railway.app}
echo "Using hostname: $HOSTNAME"

# Install MeshCentral if needed
if [ ! -d "node_modules/meshcentral" ]; then
  echo "Installing MeshCentral..."
  npm install meshcentral
fi

# Create directories if they don't exist
mkdir -p meshcentral-data

# Ensure config.json is properly set up
cat > meshcentral-data/config.json << EOF
{
  "settings": {
    "cert": "$HOSTNAME",
    "certUrl": "https://$HOSTNAME",
    "port": 8443,
    "redirPort": 8080,
    "tlsOffload": true,
    "allowLoginToken": true,
    "WANonly": true,
    "exactPort": false,
    "trustedProxy": ["0.0.0.0/0"]
  },
  "domains": {
    "": {
      "title": "TreeTee",
      "newAccounts": true,
      "ipkvm": true
    }
  },
  "letsencrypt": {
    "email": "notabot@juangpt.com",
    "names": "$HOSTNAME",
    "skipChallengeVerification": true,
    "production": true
  }
}
EOF

echo "Configuration updated for hostname: $HOSTNAME"

# Install Python dependencies with virtual environment
echo "Setting up Python environment..."
python3 -m venv /tmp/venv
source /tmp/venv/bin/activate
pip install aiohttp==3.8.5 cryptography

# Start MeshCentral in the background
echo "Starting MeshCentral server..."
node ./node_modules/meshcentral &
MESH_PID=$!

# Give MeshCentral time to start
echo "Waiting for MeshCentral to initialize..."
sleep 10

# Start the redirect handler
echo "Starting redirect handler..."
python3 redirect_handler.py &
REDIRECT_PID=$!

# Log the PIDs
echo "MeshCentral running with PID: $MESH_PID"
echo "Redirect handler running with PID: $REDIRECT_PID"

# Handle signals
trap "echo 'Shutting down services...'; kill $MESH_PID $REDIRECT_PID; exit" SIGINT SIGTERM

# Keep the script running
echo "Services running. Press Ctrl+C to stop."
wait $MESH_PID $REDIRECT_PID 