# macOS "No Software to Install" Error - Fix Guide

## The Problem

When downloading the MeshCentral macOS .pkg installer, you get:
> "The package contains no software to install"

## Root Cause

MeshCentral dynamically generates the .pkg installer with your specific mesh ID embedded. The download link requires you to be **logged into the web UI** to work properly.

## Solution Methods

### Method 1: Download While Logged In (Recommended)

**Steps:**

1. **Login to TreeTee** at https://tee.up.railway.app
2. Navigate to **My Account** → **Device Groups**
3. Click **"Install"** next to your device group
4. Select **"Apple macOS"** tab
5. **Stay logged in** in the browser
6. Click **"Download .pkg"** or use the download link
7. The .pkg will download correctly with mesh ID embedded
8. Install: `sudo installer -pkg meshagent.pkg -target /`

**Why this works**: The download requires authentication cookies from your logged-in session.

### Method 2: Use Installation Assistant Link

**Steps:**

1. Login at https://tee.up.railway.app
2. Go to **My Account** → **Device Groups** → **Install** → **Apple macOS**
3. Look for **"Assistant"** or **"Installation Assistant"** link
4. Click it - this opens a special page with a download button
5. Download and install from that page

### Method 3: Manual Installation (Advanced)

If the .pkg still doesn't work, you can manually install the agent:

**On the Mac:**

```bash
# 1. Create installation directory
sudo mkdir -p /usr/local/mesh_services/meshagent

# 2. Download the agent binary
# Replace MESH_ID with your actual mesh ID from the web UI
curl -o meshagent 'https://tee.up.railway.app/meshagents?id=16&meshid=YOUR_MESH_ID_HERE'

# 3. Download the mesh configuration
curl -o meshagent.msh 'https://tee.up.railway.app/meshsettings?id=YOUR_MESH_ID_HERE'

# 4. Move files to installation directory
sudo mv meshagent /usr/local/mesh_services/meshagent/
sudo mv meshagent.msh /usr/local/mesh_services/meshagent/

# 5. Make agent executable
sudo chmod 755 /usr/local/mesh_services/meshagent/meshagent

# 6. Install as service
cd /usr/local/mesh_services/meshagent
sudo ./meshagent -fullinstall
```

### Method 4: Get Direct Download Link from Web UI

**Steps:**

1. Login to https://tee.up.railway.app
2. Navigate to device group install page
3. **Right-click** on the "Download .pkg" button
4. Select **"Copy Link Address"**
5. **Paste this URL into the Mac's browser** (while still logged in on another device)
6. Download will start with proper authentication

## Finding Your Mesh ID

Your Mesh ID is a long string shown in the installation commands. To find it:

1. Go to https://tee.up.railway.app
2. My Account → Device Groups → Install → Apple macOS
3. Look at the download URL or terminal command
4. The Mesh ID looks like: `f8uh9mSzri7adGdnV7P3xlvdxkqClQtWa$kTSVqjDpX65IA1WjmXVz5JEqn71Qm`

It's usually in a URL like:
```
https://tee.up.railway.app/meshagents?id=16&meshid=YOUR_MESH_ID_HERE
```

## Debugging the .pkg File

If you downloaded a .pkg that doesn't work:

```bash
# Check if .pkg is valid
pkgutil --check-signature meshagent.pkg

# List contents of .pkg
pkgutil --payload-files meshagent.pkg

# Expand .pkg to see what's inside
pkgutil --expand meshagent.pkg ./expanded_pkg
ls -la ./expanded_pkg

# Check file size (should be several MB)
ls -lh meshagent.pkg
```

**If the .pkg is very small (< 100KB)**, it's likely an error page, not the actual installer.

## Alternative: Use Browser Developer Tools

**For tech-savvy users:**

1. Login to https://tee.up.railway.app
2. Open browser Developer Tools (F12)
3. Go to **Network** tab
4. Click **"Download .pkg"**
5. Find the download request in Network tab
6. Right-click → **Copy as cURL**
7. Run that curl command on the Mac (it includes authentication headers)

## Workaround Script

Save this as `mac-agent-install.sh` and run on your Mac:

```bash
#!/bin/bash

echo "=== MeshCentral macOS Agent Manual Installation ==="
echo ""
echo "You need two pieces of information from the web UI:"
echo "1. Your Mesh ID"
echo "2. The server URL (https://tee.up.railway.app)"
echo ""

read -p "Enter your Mesh ID: " MESH_ID
SERVER_URL="https://tee.up.railway.app"

echo ""
echo "Downloading agent binary..."
curl -L -o meshagent "${SERVER_URL}/meshagents?id=16&meshid=${MESH_ID}"

echo "Downloading agent configuration..."
curl -L -o meshagent.msh "${SERVER_URL}/meshsettings?id=${MESH_ID}"

# Check if downloads were successful
if [ ! -f "meshagent" ] || [ ! -f "meshagent.msh" ]; then
    echo "Error: Download failed. Make sure your Mesh ID is correct."
    exit 1
fi

# Check file sizes
AGENT_SIZE=$(stat -f%z meshagent 2>/dev/null || stat -c%s meshagent 2>/dev/null)
if [ "$AGENT_SIZE" -lt 1000000 ]; then
    echo "Error: Downloaded agent file is too small. This might be an error page."
    echo "You may need to be logged into the web UI to download."
    exit 1
fi

echo "Creating installation directory..."
sudo mkdir -p /usr/local/mesh_services/meshagent

echo "Installing files..."
sudo mv meshagent /usr/local/mesh_services/meshagent/
sudo mv meshagent.msh /usr/local/mesh_services/meshagent/
sudo chmod 755 /usr/local/mesh_services/meshagent/meshagent

echo "Installing as service..."
cd /usr/local/mesh_services/meshagent
sudo ./meshagent -fullinstall

echo ""
echo "Installation complete!"
echo "Check if the agent is running:"
echo "  sudo launchctl list | grep mesh"
echo ""
echo "The device should appear in your web UI within 30 seconds."
```

## Why This Happens

MeshCentral's macOS installer is **dynamically generated** because:

1. Each .pkg is customized with your specific mesh group ID
2. The server embeds connection info into the installer
3. This prevents generic installers that could connect anywhere

The web UI authentication ensures only authorized users can download installers for their mesh groups.

## Still Not Working?

### Check These:

1. **Login Status**: Ensure you're actually logged in when downloading
2. **Browser**: Try a different browser (Safari, Chrome, Firefox)
3. **Session**: If you logged in hours ago, try logging out and back in
4. **URL**: Make sure you're using https://tee.up.railway.app (not localhost)
5. **Mesh Group**: Verify the mesh group actually exists

### Get Installation Command Instead

Instead of downloading .pkg:

1. Go to installation page
2. Look for **"Terminal Command"** or **"Command Line"** option
3. Copy the command shown
4. **DO NOT run it directly** - the meshid in the command is what you need
5. Extract the Mesh ID from the command
6. Use Method 3 (Manual Installation) above

## Testing the Fix

After installation, verify:

```bash
# 1. Check service is loaded
sudo launchctl list | grep mesh
# Expected: Shows meshagent with a PID

# 2. Check process is running
ps aux | grep meshagent | grep -v grep
# Expected: Shows meshagent process

# 3. Check network connections
sudo lsof -i -P | grep mesh
# Expected: Shows connections to tee.up.railway.app

# 4. Check web UI
# Go to https://tee.up.railway.app
# Navigate to your device group
# Expected: Your Mac should appear in the list
```

## Common Errors and Fixes

### "Package is damaged and can't be opened"
**Fix**: Remove quarantine attribute
```bash
xattr -d com.apple.quarantine meshagent.pkg
```

### "Installation failed" with no other error
**Fix**: Check Console.app for detailed errors
```bash
open /Applications/Utilities/Console.app
# Filter for "install" or "meshagent"
```

### Agent installs but doesn't connect
**Fix**: Check the mesh configuration
```bash
sudo cat /usr/local/mesh_services/meshagent/meshagent.msh | grep -i "MeshServer"
# Should show: "MeshServer":"wss://tee.up.railway.app:443"
```

## Need to Start Fresh?

Complete removal before reinstalling:

```bash
# Stop and uninstall
sudo launchctl unload /Library/LaunchDaemons/meshagent_osx64LaunchDaemon.plist 2>/dev/null
sudo rm -rf /Library/Mesh\ Agent
sudo rm -rf /usr/local/mesh_services
sudo rm /Library/LaunchDaemons/meshagent*.plist 2>/dev/null
sudo pkgutil --forget com.meshcentral.meshagent 2>/dev/null

# Then try installation again
```

## Summary

**The key issue**: macOS .pkg downloads require an authenticated web session.

**Best solution**: Download the .pkg **while logged into the web UI** in the same browser.

**Alternative**: Use manual installation method if automated .pkg continues to fail.
