#!/bin/bash

echo "=== macOS MeshCentral Agent Detection ==="
echo ""

# Detect architecture
ARCH=$(uname -m)
echo "Architecture: $ARCH"

# Detect macOS version
MACOS_VERSION=$(sw_vers -productVersion)
echo "macOS Version: $MACOS_VERSION"

# Get detailed CPU info
CPU_BRAND=$(sysctl -n machdep.cpu.brand_string)
echo "CPU: $CPU_BRAND"

# Detect chip type
if [ "$ARCH" == "arm64" ]; then
    CHIP_TYPE="Apple Silicon"
    RECOMMENDED_ID="16 (Universal) or 29 (ARM-specific)"
else
    CHIP_TYPE="Intel"
    RECOMMENDED_ID="16 (Universal) or 3 (Intel-specific)"
fi

echo "Chip Type: $CHIP_TYPE"
echo ""
echo "=== Recommended Agent ==="
echo "Agent ID: $RECOMMENDED_ID"
echo "Binary: meshagent_osx-universal-64 (works on both architectures)"
echo ""

# Check if agent is already installed
echo "=== Installation Status ==="
if [ -d "/usr/local/mesh_services/meshagent" ] || [ -d "/Library/Mesh Agent" ]; then
    echo "✓ MeshAgent appears to be installed"

    # Find installation location
    if [ -d "/Library/Mesh Agent" ]; then
        INSTALL_PATH="/Library/Mesh Agent"
    else
        INSTALL_PATH="/usr/local/mesh_services/meshagent"
    fi
    echo "  Location: $INSTALL_PATH"

    # Check if service is running
    if sudo launchctl list | grep -q mesh; then
        echo "✓ MeshAgent service is running"
    else
        echo "✗ MeshAgent service is not running"
    fi
else
    echo "✗ MeshAgent is not installed"
fi

echo ""
echo "=== System Requirements Check ==="

# Check macOS version (MeshAgent requires 10.9+)
MACOS_MAJOR=$(echo $MACOS_VERSION | cut -d. -f1)
MACOS_MINOR=$(echo $MACOS_VERSION | cut -d. -f2)

if [ "$MACOS_MAJOR" -ge 11 ] || ([ "$MACOS_MAJOR" -eq 10 ] && [ "$MACOS_MINOR" -ge 9 ]); then
    echo "✓ macOS version is compatible (requires 10.9+)"
else
    echo "✗ macOS version too old (requires 10.9+)"
fi

# Check for curl
if command -v curl &> /dev/null; then
    echo "✓ curl is installed"
else
    echo "✗ curl not found"
fi

# Check internet connectivity
if ping -c 1 8.8.8.8 &> /dev/null; then
    echo "✓ Internet connectivity available"
else
    echo "✗ No internet connectivity"
fi

# Check if server is reachable
if curl -s -I https://tee.up.railway.app &> /dev/null; then
    echo "✓ MeshCentral server is reachable"
else
    echo "✗ Cannot reach MeshCentral server"
fi

echo ""
echo "=== Next Steps ==="
echo "1. Go to https://tee.up.railway.app"
echo "2. Login and navigate to My Account → Device Groups"
echo "3. Click 'Install' next to your device group"
echo "4. Select 'Apple macOS' tab"
echo "5. Download the .pkg file or copy the terminal command"
echo "6. Run: sudo installer -pkg meshagent.pkg -target /"
echo ""
echo "If you encounter 'unidentified developer' warning:"
echo "  Right-click the .pkg → Open → Click 'Open' again"
