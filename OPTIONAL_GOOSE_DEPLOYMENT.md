# Optional Goose AI Deployment for DaisyChain Agents

## Overview

**Goose is completely optional and separate from MeshCentral agent installation.**

This guide covers deploying Goose AI assistant to agents **after** they are successfully connected to DaisyChain. Goose installation does not interfere with or block MeshCentral agent functionality.

## Installation Flow

```
1. Install MeshCentral Agent   ✓ (Core requirement - must complete)
   └─> Agent connects to DaisyChain
   └─> Agent appears in web UI
   └─> Agent is fully functional

2. (Optional) Install Goose    ✓ (Enhancement - can be done anytime)
   └─> Goose available for AI chat
   └─> Does not affect MeshAgent
   └─> Can be installed/removed independently
```

## When to Install Goose

Install Goose on agents when:
- Agent is already connected and working in DaisyChain
- You want AI coding assistance on that machine
- The agent is used for development work
- You want to experiment with AI-assisted debugging

**Do NOT** install Goose:
- During initial agent installation
- On production servers (unless specifically needed)
- On agents where AI assistance isn't needed
- Before verifying MeshAgent connectivity

## Deployment Methods

### Method 1: Manual Installation (Recommended for Testing)

**Step 1:** Verify agent is connected in DaisyChain web UI

**Step 2:** Open Terminal for that agent in MeshCentral

**Step 3:** Run platform-specific install command:

**Linux:**
```bash
curl -fsSL https://github.com/block/goose/releases/download/stable/download_cli.sh | bash
```

**macOS:**
```bash
# Option A: Homebrew (if available)
brew install block-goose-cli

# Option B: Direct install
curl -fsSL https://github.com/block/goose/releases/download/stable/download_cli.sh | bash
```

**Windows (PowerShell):**
```powershell
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/block/goose/main/download_cli.ps1" -OutFile "$env:TEMP\install-goose.ps1"
& "$env:TEMP\install-goose.ps1"
```

**Step 4:** Configure Goose (API key, provider):
```bash
goose configure
```

### Method 2: Automated Deployment via MeshCentral Files

**Step 1:** Verify agents are connected

**Step 2:** Upload installation script via MeshCentral Files tab:
- For Linux: Upload `install-goose-linux.sh`
- For macOS: Upload `install-goose-macos.sh`
- For Windows: Upload `install-goose-windows.ps1`

**Step 3:** Run via Terminal:
```bash
# Linux/macOS
chmod +x install-goose-*.sh
./install-goose-linux.sh

# Windows
.\install-goose-windows.ps1
```

### Method 3: Batch Deployment (Multiple Agents)

Create a deployment script that runs on multiple agents:

```bash
#!/bin/bash
# deploy-goose-to-agents.sh

# This script assumes agents are already connected to DaisyChain
# and you want to bulk-install Goose

AGENTS=("agent1.example.com" "agent2.example.com" "agent3.example.com")

for agent in "${AGENTS[@]}"; do
    echo "Installing Goose on $agent..."

    # Use MeshCentral CLI or API to execute command on agent
    # This is pseudo-code - adapt to your MeshCentral setup
    mesh-execute-command "$agent" "curl -fsSL https://github.com/block/goose/releases/download/stable/download_cli.sh | bash"

    echo "Goose installed on $agent"
done
```

**Note:** MeshCentral CLI/API commands depend on your specific setup. See MeshCentral documentation for remote command execution.

## Pre-configuring Goose (Optional)

To deploy Goose with a shared configuration:

### Create Shared Configuration File

```yaml
# shared-goose-config.yaml
default:
  provider: anthropic
  processor: claude-sonnet-4-20250514
  api_key_env: GOOSE_ANTHROPIC_KEY  # Use environment variable

local:
  provider: openai
  api_base: http://hugo:11434/v1  # Ollama on Tailscale
  processor: llama3
  api_key: none
```

### Deploy Configuration

```bash
# install-goose-with-config.sh

#!/bin/bash

# Step 1: Install Goose (non-blocking)
curl -fsSL https://github.com/block/goose/releases/download/stable/download_cli.sh | bash

# Step 2: Create config directory
mkdir -p ~/.config/goose

# Step 3: Download shared config
curl -o ~/.config/goose/profiles.yaml https://your-server.com/shared-goose-config.yaml

# Step 4: Set API key from environment (if using shared keys)
# Option A: Read from file deployed separately
if [ -f ~/.goose-api-key ]; then
    export GOOSE_ANTHROPIC_KEY=$(cat ~/.goose-api-key)
fi

# Option B: Use existing environment variable
# (set via shell profile or MeshCentral environment injection)

echo "Goose installed and configured"
goose --version
```

## Verification

After installation, verify Goose is working:

```bash
# Check version
goose --version

# Check configuration exists
ls -la ~/.config/goose/profiles.yaml

# Test with a quick session
goose session start
> "hello"
> exit
```

## Removal

If you need to remove Goose from an agent:

**Linux/macOS:**
```bash
# Remove binary
rm -f ~/.local/bin/goose

# Remove configuration
rm -rf ~/.config/goose

# Remove cache
rm -rf ~/.cache/goose
```

**Windows:**
```powershell
# Remove installation directory
Remove-Item -Recurse -Force "$env:USERPROFILE\.goose"

# Remove configuration
Remove-Item -Recurse -Force "$env:USERPROFILE\.config\goose"
```

**MeshCentral Agent is NOT affected by removing Goose.**

## Integration Points

### Non-Blocking Design

Goose installation:
- ✓ Runs independently of MeshAgent
- ✓ Does not require agent restart
- ✓ Does not modify agent configuration
- ✓ Can be installed/removed without affecting connectivity
- ✓ Failures do not impact agent functionality

### Separation of Concerns

| Component | Purpose | Installation | Dependencies |
|-----------|---------|--------------|--------------|
| **MeshAgent** | Remote management, monitoring | Required, install first | None |
| **Goose** | AI coding assistant | Optional, install after | MeshAgent working |

## Best Practices

1. **Always install MeshAgent first**
   - Verify agent connectivity in DaisyChain UI
   - Confirm agent can execute commands
   - Test terminal access works

2. **Install Goose as enhancement**
   - Only on agents where it's needed
   - After agent is stable and connected
   - Test on one agent before bulk deployment

3. **Configuration management**
   - Use environment variables for API keys
   - Never commit API keys to git
   - Use shared configs for consistency

4. **Monitoring**
   - Track which agents have Goose installed
   - Monitor API usage costs
   - Document configuration per agent

## Troubleshooting

### Goose Installation Fails

**This does NOT affect MeshAgent:**
- Agent remains connected to DaisyChain
- All MeshCentral functions still work
- Simply retry Goose installation later

**Common fixes:**
```bash
# Check internet connectivity
ping github.com

# Check disk space
df -h

# Verify write permissions
ls -la ~/.local/bin
ls -la ~/.config

# Re-run installation
curl -fsSL https://github.com/block/goose/releases/download/stable/download_cli.sh | bash
```

### Goose Doesn't Start

```bash
# Verify installation
which goose

# Check configuration
cat ~/.config/goose/profiles.yaml

# Test with verbose output
goose session start --verbose

# Reconfigure
goose configure
```

## Example Deployment Workflow

```bash
# 1. Verify agent is connected (check DaisyChain web UI)
# Agent "dev-server-01" is online and responsive

# 2. Open Terminal for agent in MeshCentral

# 3. Install Goose (non-blocking, optional)
curl -fsSL https://github.com/block/goose/releases/download/stable/download_cli.sh | bash

# 4. Configure Goose
goose configure
# Choose: Anthropic
# Enter API key: sk-ant-...
# Select model: claude-sonnet-4

# 5. Test Goose
goose session start
> "What version of Python is installed?"
> exit

# 6. Document installation
echo "dev-server-01: Goose installed, Anthropic provider" >> goose-deployments.txt

# MeshAgent remains unaffected throughout
```

## Summary

✓ **Goose is completely optional**
✓ **Install after MeshAgent is working**
✓ **Non-blocking - failures don't affect agent**
✓ **Can be added/removed independently**
✓ **Enhances development workflow without impacting core functionality**

---

**DaisyChain agents work perfectly without Goose. Goose is just a bonus AI feature.**
