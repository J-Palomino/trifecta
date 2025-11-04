# MeshCentral API Guide for Programmatic Agent Control

## Overview

MeshCentral provides multiple ways to programmatically send commands to agents:
1. **WebSocket API** (primary method)
2. **MeshCtrl CLI** (official command-line tool)
3. **Meshbook** (community YAML-based tool)
4. **Web UI Scripts** (preConfiguredScripts - what we just implemented!)

## Important: WebSocket-Based, Not REST

**MeshCentral makes almost no use of RESTful APIs.** Instead, almost everything is done using WebSocket with JSON messages.

## Method 1: WebSocket API (Most Powerful)

### Primary Endpoint

```
wss://tee.up.railway.app/control.ashx
```

### Architecture

- **Full duplex communication** via WebSocket
- **JSON messages** for all operations
- **Authentication** via user credentials
- **Real-time responses** from agents

### Connection Flow

```
1. Connect to wss://your-server/control.ashx
2. Send authentication message with username/password
3. Receive authentication response
4. Send command messages to agents
5. Receive responses from agents
6. Maintain connection or close
```

### Example: Node.js WebSocket Client

```javascript
const WebSocket = require('ws');

// Connect to MeshCentral
const ws = new WebSocket('wss://tee.up.railway.app/control.ashx');

ws.on('open', () => {
    console.log('Connected to MeshCentral');

    // Authenticate
    const authMessage = {
        action: 'authcookie',
        cookie: 'your-auth-cookie-here',
        domain: ''
    };

    ws.send(JSON.stringify(authMessage));
});

ws.on('message', (data) => {
    const message = JSON.parse(data);
    console.log('Received:', message);

    // Handle different message types
    if (message.action === 'authcookie') {
        console.log('Authenticated!');

        // Send command to agent
        const commandMessage = {
            action: 'runcommands',
            nodeids: ['node//DEVICE_ID_HERE'],
            type: 0,  // 0=Linux/macOS shell, 1=Windows command, 2=Windows PowerShell
            cmds: 'echo "Hello from API"',
            runAsUser: 1  // 1=run as user, 0=run as agent
        };

        ws.send(JSON.stringify(commandMessage));
    }

    if (message.action === 'runcommands') {
        console.log('Command result:', message.result);
    }
});

ws.on('error', (error) => {
    console.error('WebSocket error:', error);
});

ws.on('close', () => {
    console.log('Disconnected from MeshCentral');
});
```

### Message Types

**Authentication:**
```json
{
  "action": "authcookie",
  "cookie": "your-auth-cookie",
  "domain": ""
}
```

**Run Command:**
```json
{
  "action": "runcommands",
  "nodeids": ["node//DEVICE_ID"],
  "type": 0,
  "cmds": "your-command-here",
  "runAsUser": 1
}
```

**Get Nodes (Devices):**
```json
{
  "action": "nodes"
}
```

### Command Types

| Type | Platform | Description |
|------|----------|-------------|
| `0` | Linux/macOS | Shell command |
| `1` | Windows | cmd.exe command |
| `2` | Windows | PowerShell command |

### Getting Auth Cookie

**Method 1: From Browser**
1. Login to DaisyChain web UI
2. Open Developer Tools (F12)
3. Go to Application → Cookies
4. Find cookie starting with "mesh"
5. Copy the value

**Method 2: Programmatic Login**
```javascript
// HTTP POST to /login
const response = await fetch('https://tee.up.railway.app/login', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: new URLSearchParams({
        username: 'your-username',
        password: 'your-password'
    })
});

// Extract cookie from response headers
const setCookie = response.headers.get('set-cookie');
```

## Method 2: MeshCtrl CLI (Official Tool)

### Installation

```bash
npm install meshctrl -g
```

### Configuration

```bash
# Add your MeshCentral server
meshctrl AddServer --url https://tee.up.railway.app --name DaisyChain

# Login with credentials
meshctrl Login --name DaisyChain --user yourUsername --pass yourPassword
```

### Running Commands

**Single Device:**
```bash
# Run command on specific device
meshctrl RunCommand --id DEVICE_ID --cmd "echo 'Hello from MeshCtrl'"

# Run shell script
meshctrl RunCommand --id DEVICE_ID --cmd "bash -c 'df -h && free -h'"
```

**Multiple Devices:**
```bash
# Run on all devices in a group
meshctrl RunCommand --group GROUP_ID --cmd "uptime"
```

**Install Goose via MeshCtrl:**
```bash
# Install Goose on a specific device
meshctrl RunCommand --id DEVICE_ID --cmd "curl -fsSL https://github.com/block/goose/releases/download/stable/download_cli.sh | bash"

# Check Goose status on all Linux devices
meshctrl RunCommand --group LINUX_GROUP --cmd "goose --version 2>/dev/null || echo 'Not installed'"
```

### MeshCtrl Commands Reference

```bash
# List all devices
meshctrl ListDevices

# List device groups
meshctrl ListDeviceGroups

# Get device details
meshctrl ShowDevice --id DEVICE_ID

# Upload file to device
meshctrl Upload --id DEVICE_ID --local local-file.txt --remote /tmp/remote-file.txt

# Download file from device
meshctrl Download --id DEVICE_ID --remote /var/log/syslog --local ./syslog

# Get device power state
meshctrl PowerState --id DEVICE_ID

# Wake device
meshctrl Wake --id DEVICE_ID
```

## Method 3: Meshbook (YAML-Based Automation)

### Installation

```bash
npm install -g meshbook
```

### Configuration

Create `meshbook.yaml`:

```yaml
meshcentral:
  url: https://tee.up.railway.app
  username: yourUsername
  password: yourPassword

tasks:
  install-goose:
    description: Install Goose AI on all Linux agents
    devices:
      - group: "Linux Servers"
    commands:
      - type: shell
        command: curl -fsSL https://github.com/block/goose/releases/download/stable/download_cli.sh | bash
        runAsUser: true

  check-goose:
    description: Check Goose status on all devices
    devices:
      - group: "Development Servers"
    commands:
      - type: shell
        command: |
          if command -v goose &> /dev/null; then
            goose --version
          else
            echo "Goose not installed"
          fi
        runAsUser: true

  deploy-goose-config:
    description: Deploy Goose configuration to agents
    devices:
      - id: DEVICE_ID_1
      - id: DEVICE_ID_2
    commands:
      - type: shell
        command: |
          mkdir -p ~/.config/goose
          cat > ~/.config/goose/profiles.yaml <<'EOF'
          default:
            provider: anthropic
            processor: claude-sonnet-4
            api_key_env: GOOSE_API_KEY
          EOF
        runAsUser: true
```

### Run Tasks

```bash
# Run specific task
meshbook run --task install-goose

# Run all tasks
meshbook run --all

# Dry run (show what would execute)
meshbook run --task install-goose --dry-run
```

## Method 4: PreConfigured Scripts (Web UI)

**What we just implemented!** This is the simplest method for end users.

### Configuration (Already Done)

In `meshcentral-data/config.json.template`:

```json
{
  "domains": {
    "": {
      "preConfiguredScripts": [
        {
          "name": "Install Goose AI (Linux)",
          "cmd": "curl -fsSL https://github.com/block/goose/releases/download/stable/download_cli.sh | bash",
          "type": "sh",
          "runas": "user"
        }
      ]
    }
  }
}
```

### Usage

1. Login to DaisyChain web UI
2. Select device
3. Actions → Run Commands
4. Click script name
5. Done!

## Use Cases and Examples

### Use Case 1: Automated Goose Deployment

**Scenario:** Deploy Goose to all development servers

**Using MeshCtrl:**
```bash
# Get group ID
GROUP_ID=$(meshctrl ListDeviceGroups | grep "Dev Servers" | cut -d' ' -f1)

# Install Goose on all devices in group
meshctrl RunCommand --group $GROUP_ID --cmd "curl -fsSL https://github.com/block/goose/releases/download/stable/download_cli.sh | bash"

# Verify installation
meshctrl RunCommand --group $GROUP_ID --cmd "goose --version"
```

**Using Meshbook:**
```yaml
tasks:
  mass-goose-deploy:
    devices:
      - group: "Dev Servers"
      - group: "QA Servers"
    commands:
      - type: shell
        command: curl -fsSL https://github.com/block/goose/releases/download/stable/download_cli.sh | bash
        runAsUser: true
```

### Use Case 2: Health Check All Agents

**Using WebSocket API:**
```javascript
const healthCheck = {
    action: 'runcommands',
    nodeids: allDeviceIds,  // Array of all device IDs
    type: 0,
    cmds: 'uptime && df -h && free -h',
    runAsUser: 0
};

ws.send(JSON.stringify(healthCheck));
```

**Using MeshCtrl:**
```bash
meshctrl ListDevices --json | jq -r '.[].id' | while read id; do
    echo "Checking $id..."
    meshctrl RunCommand --id "$id" --cmd "uptime"
done
```

### Use Case 3: Distribute Configuration Files

**Using MeshCtrl:**
```bash
# Upload Goose config to multiple devices
DEVICES="DEVICE_ID_1 DEVICE_ID_2 DEVICE_ID_3"

for device in $DEVICES; do
    meshctrl Upload --id "$device" --local ./goose-config.yaml --remote ~/.config/goose/profiles.yaml
done
```

**Using WebSocket API:**
```javascript
// Upload file content
const uploadMessage = {
    action: 'upload',
    nodeids: ['node//DEVICE_ID'],
    path: '~/.config/goose/profiles.yaml',
    content: Buffer.from(configContent).toString('base64')
};
```

### Use Case 4: Interactive Goose Session Automation

**Scenario:** Start Goose and send initial prompt

**Using MeshCtrl:**
```bash
# Start Goose with predefined prompt
meshctrl RunCommand --id DEVICE_ID --cmd "echo 'help me audit this system for security issues' | goose session start"
```

## Integration with FastAPI

### Example: FastAPI Endpoint to Install Goose

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import websockets
import json
import asyncio

app = FastAPI()

class GooseInstallRequest(BaseModel):
    device_id: str
    meshcentral_url: str = "wss://tee.up.railway.app/control.ashx"
    auth_cookie: str

@app.post("/install-goose")
async def install_goose(request: GooseInstallRequest):
    """Install Goose on a MeshCentral-managed device via WebSocket API"""

    try:
        async with websockets.connect(request.meshcentral_url) as ws:
            # Authenticate
            auth_msg = {
                "action": "authcookie",
                "cookie": request.auth_cookie,
                "domain": ""
            }
            await ws.send(json.dumps(auth_msg))

            # Wait for auth response
            auth_response = json.loads(await ws.recv())
            if auth_response.get("action") != "authcookie":
                raise HTTPException(status_code=401, detail="Authentication failed")

            # Send install command
            install_cmd = {
                "action": "runcommands",
                "nodeids": [f"node//{request.device_id}"],
                "type": 0,  # Shell command
                "cmds": "curl -fsSL https://github.com/block/goose/releases/download/stable/download_cli.sh | bash",
                "runAsUser": 1
            }
            await ws.send(json.dumps(install_cmd))

            # Wait for response
            result = json.loads(await ws.recv())

            return {
                "status": "success",
                "message": "Goose installation initiated",
                "result": result
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/goose-status/{device_id}")
async def check_goose_status(device_id: str, auth_cookie: str):
    """Check if Goose is installed on a device"""

    async with websockets.connect("wss://tee.up.railway.app/control.ashx") as ws:
        # Auth
        await ws.send(json.dumps({
            "action": "authcookie",
            "cookie": auth_cookie,
            "domain": ""
        }))
        await ws.recv()

        # Check Goose
        await ws.send(json.dumps({
            "action": "runcommands",
            "nodeids": [f"node//{device_id}"],
            "type": 0,
            "cmds": "command -v goose && goose --version || echo 'Not installed'",
            "runAsUser": 1
        }))

        result = json.loads(await ws.recv())
        return {"status": "success", "output": result}
```

## Security Considerations

### Authentication

- **Never hardcode credentials** in scripts
- **Use environment variables** for sensitive data
- **Rotate auth cookies** regularly
- **Use least-privilege accounts**

### Command Injection

```javascript
// BAD - vulnerable to injection
const userInput = req.body.command;
const cmd = {
    action: 'runcommands',
    cmds: userInput  // DANGEROUS!
};

// GOOD - validate and sanitize
const allowedCommands = ['goose status', 'goose --version', 'uptime'];
if (!allowedCommands.includes(userInput)) {
    throw new Error('Command not allowed');
}
```

### Network Security

- **Use WSS (WebSocket Secure)** - not WS
- **Verify TLS certificates**
- **Use VPN (Tailscale)** for additional security
- **Whitelist IPs** if possible

## Deployment to Railway

### Environment Variables

Add to Railway dashboard:

```bash
MESHCENTRAL_API_USER=api-automation-user
MESHCENTRAL_API_PASS=secure-password-here
```

### Accessing from Railway Services

```javascript
// In another Railway service
const MESHCENTRAL_URL = 'wss://tee.up.railway.app/control.ashx';
const API_USER = process.env.MESHCENTRAL_API_USER;
const API_PASS = process.env.MESHCENTRAL_API_PASS;

// Connect and authenticate
// ... (use examples above)
```

## Monitoring and Logging

### Log Command Execution

```javascript
ws.on('message', (data) => {
    const message = JSON.parse(data);

    // Log all command results
    if (message.action === 'runcommands') {
        console.log(`[${new Date().toISOString()}] Command result:`, {
            device: message.nodeid,
            command: message.cmd,
            result: message.result,
            exitCode: message.exitcode
        });

        // Send to logging service
        logToService({
            timestamp: Date.now(),
            device: message.nodeid,
            command: message.cmd,
            success: message.exitcode === 0
        });
    }
});
```

## Best Practices

1. **Use MeshCtrl for ad-hoc commands**
2. **Use Meshbook for scheduled/repeated tasks**
3. **Use WebSocket API for real-time integrations**
4. **Use PreConfigured Scripts for end-user actions**
5. **Always validate device IDs** before sending commands
6. **Implement retry logic** for failed commands
7. **Log all automation activities**
8. **Test on one device** before bulk operations

## Resources

- **MeshCtrl Documentation**: https://meshcentral.com/docs/MeshCtrlUsersGuide.pdf
- **Meshbook GitHub**: https://github.com/DaanSelen/meshbook
- **MeshCentral Architecture**: https://meshcentral.com/docs/MeshCentral2DesignArchitecture.pdf
- **WebSocket Examples**: See MeshCentral GitHub for more examples

---

**DaisyChain now supports programmatic agent control via WebSocket API, MeshCtrl CLI, Meshbook automation, and web UI buttons!**
