#!/bin/bash

echo "=== MeshCentral macOS Agent Manual Installation ==="
echo ""
echo "This script manually installs the MeshCentral agent on macOS."
echo "Use this if the .pkg installer gives 'no software to install' error."
echo ""
echo "You need your Mesh ID from: https://tee.up.railway.app"
echo "Go to: My Account → Device Groups → Install → Apple macOS"
echo ""

read -p "Enter your Mesh ID: " MESH_ID

if [ -z "$MESH_ID" ]; then
    echo "Error: Mesh ID cannot be empty"
    exit 1
fi

SERVER_URL="https://tee.up.railway.app"

echo ""
echo "=== Downloading Files ==="

# Detect architecture
ARCH=$(uname -m)
if [ "$ARCH" == "arm64" ]; then
    AGENT_ID="16"  # Universal binary (works on both)
    echo "Detected: Apple Silicon (M1/M2/M3)"
else
    AGENT_ID="16"  # Universal binary (works on both)
    echo "Detected: Intel Mac"
fi

echo "Using Universal agent (works on all Macs)"
echo ""

# Download agent binary
echo "Downloading agent binary..."
if ! curl -f -L -o meshagent "${SERVER_URL}/meshagents?id=${AGENT_ID}&meshid=${MESH_ID}"; then
    echo "Error: Failed to download agent binary"
    echo "Check that your Mesh ID is correct and try again"
    exit 1
fi

# Download agent configuration
echo "Downloading agent configuration..."
if ! curl -f -L -o meshagent.msh "${SERVER_URL}/meshsettings?id=${MESH_ID}"; then
    echo "Error: Failed to download agent configuration"
    echo "Check that your Mesh ID is correct and try again"
    rm -f meshagent
    exit 1
fi

echo ""
echo "=== Validating Downloads ==="

# Check if files exist
if [ ! -f "meshagent" ] || [ ! -f "meshagent.msh" ]; then
    echo "Error: Download failed"
    exit 1
fi

# Check agent file size
AGENT_SIZE=$(stat -f%z meshagent 2>/dev/null || stat -c%s meshagent 2>/dev/null)
if [ "$AGENT_SIZE" -lt 1000000 ]; then
    echo "Error: Downloaded agent file is too small ($AGENT_SIZE bytes)"
    echo "This might be an error page instead of the actual agent."
    echo ""
    echo "Try these solutions:"
    echo "1. Login to https://tee.up.railway.app in your browser"
    echo "2. Keep that browser window open"
    echo "3. Run this script again"
    rm -f meshagent meshagent.msh
    exit 1
fi

echo "✓ Agent binary: $(echo "scale=1; $AGENT_SIZE/1024/1024" | bc) MB"

# Check config file size
MSH_SIZE=$(stat -f%z meshagent.msh 2>/dev/null || stat -c%s meshagent.msh 2>/dev/null)
echo "✓ Configuration: $(echo "scale=1; $MSH_SIZE/1024" | bc) KB"

# Verify configuration contains server URL
if ! grep -q "tee.up.railway.app" meshagent.msh; then
    echo "Warning: Configuration doesn't contain expected server URL"
    echo "Installation may not work correctly"
fi

echo ""
echo "=== Installing Agent ==="

# Check if already installed
if [ -d "/usr/local/mesh_services/meshagent" ] || [ -d "/Library/Mesh Agent" ]; then
    echo "Found existing installation"
    read -p "Remove existing installation? (y/n): " REMOVE
    if [ "$REMOVE" == "y" ] || [ "$REMOVE" == "Y" ]; then
        echo "Removing existing installation..."
        sudo launchctl unload /Library/LaunchDaemons/meshagent_osx64LaunchDaemon.plist 2>/dev/null
        sudo launchctl unload /Library/LaunchDaemons/meshagent.plist 2>/dev/null
        sudo rm -rf /Library/Mesh\ Agent
        sudo rm -rf /usr/local/mesh_services/meshagent
        sudo rm /Library/LaunchDaemons/meshagent*.plist 2>/dev/null
        echo "✓ Removed existing installation"
    else
        echo "Keeping existing installation. Installation may fail."
    fi
fi

# Create installation directory
echo "Creating installation directory..."
sudo mkdir -p /usr/local/mesh_services/meshagent

# Install files
echo "Installing agent files..."
sudo cp meshagent /usr/local/mesh_services/meshagent/
sudo cp meshagent.msh /usr/local/mesh_services/meshagent/
sudo chmod 755 /usr/local/mesh_services/meshagent/meshagent

# Clean up downloaded files
rm -f meshagent meshagent.msh

echo "Installing as system service..."
cd /usr/local/mesh_services/meshagent

# Run full installation
if sudo ./meshagent -fullinstall; then
    echo "✓ Service installed successfully"
else
    echo "Error: Service installation failed"
    echo "Check the output above for error messages"
    exit 1
fi

echo ""
echo "=== Verifying Installation ==="

# Wait a moment for service to start
sleep 2

# Check if service is loaded
if sudo launchctl list | grep -q mesh; then
    echo "✓ MeshAgent service is loaded"
else
    echo "✗ MeshAgent service is not loaded"
fi

# Check if process is running
if ps aux | grep meshagent | grep -v grep > /dev/null; then
    echo "✓ MeshAgent process is running"

    # Get process details
    PID=$(ps aux | grep meshagent | grep -v grep | awk '{print $2}' | head -1)
    echo "  Process ID: $PID"
else
    echo "✗ MeshAgent process is not running"
    echo "  Try manually starting: sudo launchctl load /Library/LaunchDaemons/meshagent_osx64LaunchDaemon.plist"
fi

echo ""
echo "=== Installation Complete! ==="
echo ""
echo "Next steps:"
echo "1. Go to https://tee.up.railway.app"
echo "2. Navigate to your device group"
echo "3. Your Mac should appear in the device list within 30-60 seconds"
echo ""
echo "If it doesn't appear, check logs:"
echo "  sudo launchctl list | grep mesh"
echo "  ps aux | grep meshagent"
echo "  sudo lsof -i -P | grep mesh"
echo ""
echo "To uninstall:"
echo "  sudo /usr/local/mesh_services/meshagent/meshagent -uninstall"
