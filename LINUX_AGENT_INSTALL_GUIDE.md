# MeshCentral Linux Agent Installation Guide

## How Installation Options Are Automatically Detected

The MeshCentral Linux installation script automatically detects your system architecture and downloads the correct agent binary. You don't need to manually choose - the script does it for you!

## Before Installing: Check Your System

To see what will be installed on your Linux machine, run these commands:

### 1. Check Architecture
```bash
uname -m
```

**Output Examples:**
- `x86_64` or `amd64` = 64-bit Intel/AMD processor
- `i686`, `i586`, `x86` = 32-bit Intel/AMD processor
- `armv7l` = ARM 32-bit (like Raspberry Pi 2/3/4)
- `armv6l` = ARM 32-bit (like Raspberry Pi 1)
- `aarch64` = ARM 64-bit
- `mips` = MIPS processor (routers, embedded devices)

### 2. Check OS Bit Length
```bash
getconf LONG_BIT
```

**Output:**
- `64` = 64-bit operating system
- `32` = 32-bit operating system

### 3. Check Init System
```bash
ps -p 1 -o comm=
```

**Output:**
- `systemd` = Modern Linux (Ubuntu 16+, Debian 8+, CentOS 7+, etc.)
- `init` = Older systems (uses upstart or init.d)

## Supported Agent Types (Machine IDs)

The installation script maps your system to one of these agent types:

| Machine ID | Architecture | OS Type | Examples |
|------------|-------------|---------|----------|
| 5 | x86 32-bit | Linux | Older 32-bit Intel/AMD systems |
| 6 | x86 64-bit | Linux | Modern Intel/AMD servers, desktops |
| 9 | ARM 32-bit | Linux | ARM devices (soft float) |
| 25 | ARM 32-bit HF | Linux | Raspberry Pi 2/3/4, ARM boards |
| 26 | ARM 64-bit | Linux | Modern ARM servers, Pi 4 64-bit OS |
| 30 | x86 64-bit | FreeBSD | FreeBSD systems |
| 31 | x86 32-bit | FreeBSD | FreeBSD 32-bit systems |
| 45 | RISC-V 64-bit | Linux | RISC-V processors |

## Quick Detection Script

Save this as `detect-mesh-agent.sh` and run it on your target Linux machine:

```bash
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
        else
            echo "Machine ID: 5 (Linux x86 32-bit)"
        fi
        ;;
    i686|i586|x86)
        echo "Machine ID: 5 (Linux x86 32-bit)"
        ;;
    armv7l)
        echo "Machine ID: 25 (ARM 32-bit HardFloat - Raspberry Pi)"
        ;;
    armv6l)
        echo "Machine ID: 25 (ARM 32-bit HardFloat - Raspberry Pi 1)"
        ;;
    aarch64)
        echo "Machine ID: 26 (ARM 64-bit)"
        ;;
    mips)
        echo "Machine ID: varies (MIPS - Router/Embedded)"
        ;;
    riscv64)
        echo "Machine ID: 45 (RISC-V 64-bit)"
        ;;
    *)
        echo "Unknown architecture: $ARCH"
        echo "The install script will attempt auto-detection"
        ;;
esac

echo ""
echo "=== Ready for Installation ==="
echo "The installation script will automatically select the correct agent."
```

## Installation Process

### Step 1: Get Installation Command from Web UI

1. Go to https://tee.up.railway.app
2. Login to your account
3. Navigate to **My Account** → **Device Groups**
4. Click **Install** next to your device group
5. Select the **Linux / BSD** tab
6. Copy the installation command

### Step 2: Run on Your Linux Machine

The command will look like:
```bash
wget -q https://tee.up.railway.app/meshagents?script=1 --no-check-certificate -O ./meshinstall.sh && chmod 755 ./meshinstall.sh && sudo ./meshinstall.sh https://tee.up.railway.app 'MESH_ID_HERE'
```

### Step 3: Script Auto-Detection Process

When you run the script, it will:

1. **Detect your architecture** using `uname -m`
2. **Detect your bit length** using `getconf LONG_BIT`
3. **Determine machine ID** based on detected values
4. **Download the correct agent binary** from the server
5. **Detect init system** (systemd, upstart, or init.d)
6. **Install and start the service**

## Manual Installation (Advanced)

If you need to manually specify the machine type:

```bash
sudo ./meshinstall.sh https://tee.up.railway.app 'MESH_ID_HERE' MACHINE_ID
```

Replace `MACHINE_ID` with the appropriate number from the table above.

## Verification After Installation

### Check Service Status
```bash
# For systemd systems
sudo systemctl status meshagent

# For init.d systems
sudo service meshagent status
```

### Check Agent Logs
```bash
# View recent logs
sudo journalctl -u meshagent -n 50

# Or check log file directly
sudo cat /usr/local/mesh/meshagent.log
```

### Check Connection
```bash
# Verify the agent can reach the server
curl -I https://tee.up.railway.app
```

## Common Issues

### Issue: Wrong architecture detected
**Solution:** Manually specify the machine ID:
```bash
sudo ./meshinstall.sh https://tee.up.railway.app 'MESH_ID' 6  # For x86_64
```

### Issue: Permission denied
**Solution:** Make sure you're running with sudo:
```bash
sudo ./meshinstall.sh ...
```

### Issue: Cannot connect to server
**Solution:** Check firewall allows outbound HTTPS:
```bash
sudo ufw allow out 443/tcp  # For UFW firewall
```

## Different Linux Distributions

The agent works on all major Linux distributions:

- **Ubuntu/Debian**: Full support (systemd or init.d)
- **CentOS/RHEL/Rocky**: Full support (systemd)
- **Fedora**: Full support (systemd)
- **Arch Linux**: Full support (systemd)
- **Alpine Linux**: Supported (OpenRC)
- **Raspberry Pi OS**: Full support (systemd)
- **OpenWRT**: Supported (custom builds available)

## Summary

**You don't need to choose the installation option manually!** The script automatically:
- Detects your CPU architecture
- Determines 32-bit vs 64-bit
- Identifies your init system
- Downloads the correct agent
- Installs and starts the service

Just run the installation command from the web UI, and it handles everything automatically.
