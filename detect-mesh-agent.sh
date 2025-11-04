#!/bin/bash

echo "=== MeshCentral Agent Detection ==="
echo ""

# Detect architecture
ARCH=$(uname -m)
echo "Architecture: $ARCH"

# Detect bit length
BITS=$(getconf LONG_BIT)
echo "OS Bit Length: $BITS-bit"

# Detect init system
INIT=$(ps -p 1 -o comm=)
echo "Init System: $INIT"

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    echo "OS: $NAME $VERSION"
fi

echo ""
echo "=== Recommended Agent Type ==="

# Determine agent type
case $ARCH in
    x86_64|amd64)
        if [ "$BITS" == "64" ]; then
            echo "Machine ID: 6 (Linux x86 64-bit)"
            echo "Best for: Modern Intel/AMD servers and desktops"
        else
            echo "Machine ID: 5 (Linux x86 32-bit)"
            echo "Best for: Older 32-bit Intel/AMD systems"
        fi
        ;;
    i686|i586|x86)
        echo "Machine ID: 5 (Linux x86 32-bit)"
        echo "Best for: Older 32-bit Intel/AMD systems"
        ;;
    armv7l)
        echo "Machine ID: 25 (ARM 32-bit HardFloat)"
        echo "Best for: Raspberry Pi 2/3/4 (32-bit OS)"
        ;;
    armv6l)
        echo "Machine ID: 25 (ARM 32-bit HardFloat)"
        echo "Best for: Raspberry Pi 1/Zero"
        ;;
    aarch64)
        echo "Machine ID: 26 (ARM 64-bit)"
        echo "Best for: Raspberry Pi 4 (64-bit OS), ARM servers"
        ;;
    mips|mipsel)
        echo "Machine ID: varies (MIPS)"
        echo "Best for: Routers and embedded devices"
        ;;
    riscv64)
        echo "Machine ID: 45 (RISC-V 64-bit)"
        echo "Best for: RISC-V processors"
        ;;
    *)
        echo "Unknown architecture: $ARCH"
        echo "The install script will attempt auto-detection"
        ;;
esac

echo ""
echo "=== Installation Readiness Check ==="

# Check for sudo/root
if [ "$EUID" -ne 0 ]; then
    echo "✗ Not running as root (will need sudo for installation)"
else
    echo "✓ Running as root"
fi

# Check for wget or curl
if command -v wget &> /dev/null; then
    echo "✓ wget is installed"
elif command -v curl &> /dev/null; then
    echo "✓ curl is installed"
else
    echo "✗ Neither wget nor curl found - install one of them first"
fi

# Check internet connectivity
if ping -c 1 8.8.8.8 &> /dev/null; then
    echo "✓ Internet connectivity available"
else
    echo "✗ No internet connectivity detected"
fi

# Check if server is reachable
if command -v curl &> /dev/null; then
    if curl -s -I https://tee.up.railway.app &> /dev/null; then
        echo "✓ MeshCentral server is reachable"
    else
        echo "✗ Cannot reach MeshCentral server"
    fi
fi

echo ""
echo "=== Next Steps ==="
echo "1. Go to https://tee.up.railway.app"
echo "2. Login and navigate to My Account → Device Groups"
echo "3. Click 'Install' next to your device group"
echo "4. Select 'Linux / BSD' tab"
echo "5. Copy and run the installation command on this machine"
echo ""
echo "The installation script will automatically detect and install"
echo "the correct agent for this system."
