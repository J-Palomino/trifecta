# Goose AI Assistant Integration with TreeTee

## Overview

This guide explains how to integrate Goose AI coding assistant with TreeTee/MeshCentral, allowing you to chat with AI assistants on your monitored machines. Goose provides on-machine AI capabilities for coding assistance, debugging, and automation.

## What is Goose?

**Goose** is an open-source, extensible AI agent that goes beyond code suggestions:
- Installs, executes, edits, and tests code with any LLM
- Works with Claude 4, GPT-4, local models, and more
- On-machine execution (runs directly on your agents, not in the cloud)
- Extensible toolkit for custom capabilities
- Terminal-based chat interface

**Best for:**
- AI-assisted coding and debugging on remote machines
- Automated task execution on TreeTee agents
- Development work on monitored VMs
- Quick AI consultations without leaving your agent

## Installation Methods

### Method 1: Automated Installation Scripts (Recommended)

TreeTee provides platform-specific installation scripts:

**Linux Agents:**
```bash
# From MeshCentral Terminal:
curl -o install-goose.sh https://raw.githubusercontent.com/YOUR_USERNAME/trifecta/main/install-goose-linux.sh
chmod +x install-goose.sh
./install-goose.sh
```

**macOS Agents:**
```bash
# From MeshCentral Terminal:
curl -o install-goose.sh https://raw.githubusercontent.com/YOUR_USERNAME/trifecta/main/install-goose-macos.sh
chmod +x install-goose.sh
./install-goose.sh
```

**Windows Agents:**
```powershell
# From MeshCentral Terminal (PowerShell):
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/YOUR_USERNAME/trifecta/main/install-goose-windows.ps1" -OutFile "install-goose.ps1"
.\install-goose.ps1
```

### Method 2: Manual Installation

**Linux/macOS:**
```bash
curl -fsSL https://github.com/block/goose/releases/download/stable/download_cli.sh | bash
```

**macOS with Homebrew:**
```bash
brew install block-goose-cli
```

**Windows (PowerShell):**
```powershell
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/block/goose/main/download_cli.ps1" -OutFile "download_cli.ps1"
.\download_cli.ps1
```

## Configuration

### Initial Setup

After installation, configure Goose with your AI provider:

```bash
goose configure
```

You'll be prompted to choose:
1. **AI Provider** - Anthropic, OpenAI, OpenRouter, etc.
2. **API Key** - Your provider's API key
3. **Default Model** - e.g., claude-sonnet-4, gpt-4, etc.

### Supported AI Providers

| Provider | Best For | Cost | Setup Difficulty |
|----------|----------|------|------------------|
| **Anthropic Claude** | Best performance, tool calling | Pay-as-you-go | Easy |
| **OpenRouter** | Multiple models, easy OAuth | Varies | Very Easy |
| **Tetrate Agent Router** | Free $10 credits | Free tier + usage | Easy |
| **OpenAI GPT** | Widely available | Pay-as-you-go | Easy |
| **Local (Docker Model Runner)** | Privacy, no API costs | Free (compute only) | Medium |

### Configuration File Location

Goose stores configuration in:
- **Linux**: `~/.config/goose/profiles.yaml`
- **macOS**: `~/.config/goose/profiles.yaml`
- **Windows**: `%USERPROFILE%\.config\goose\profiles.yaml`

### Example Configuration

```yaml
default:
  provider: anthropic
  processor: claude-sonnet-4-20250514
  accelerator: claude-sonnet-4-20250514
  moderator: passive
  api_key: sk-ant-...
```

## Using Goose Through MeshCentral

### Option 1: Terminal Access

1. Open device in MeshCentral web UI
2. Click **"Terminal"** to open SSH/shell session
3. Start Goose:
   ```bash
   goose session start
   ```
4. Chat with AI directly in the terminal

### Option 2: Custom MeshCentral Commands

Add custom buttons to MeshCentral for quick Goose access.

**Add to config.json.template:**
```json
{
  "domains": {
    "": {
      "title": "TreeTee",
      "userAllowedIP": "0.0.0.0/0",
      "customui": {
        "deviceButtons": [
          {
            "title": "Start Goose AI",
            "command": "goose session start",
            "description": "Launch Goose AI coding assistant"
          },
          {
            "title": "Goose Status",
            "command": "goose --version && test -f ~/.config/goose/profiles.yaml && echo 'Configured' || echo 'Not configured'",
            "description": "Check if Goose is installed and configured"
          }
        ]
      }
    }
  }
}
```

**Note**: Custom UI buttons may require MeshCentral Pro or specific versions. Check MeshCentral documentation for availability.

### Option 3: Quick Commands via Files

Create a helper script on each agent:

**Linux/macOS** (`~/start-goose.sh`):
```bash
#!/bin/bash
echo "Starting Goose AI Assistant..."
echo "Type 'exit' or press Ctrl+D to quit"
goose session start
```

**Windows** (`%USERPROFILE%\start-goose.bat`):
```batch
@echo off
echo Starting Goose AI Assistant...
echo Type 'exit' or press Ctrl+D to quit
goose session start
```

Then from MeshCentral terminal: `./start-goose.sh` or `start-goose.bat`

## Pre-configuring Goose for Multiple Agents

### Centralized Configuration Approach

To deploy Goose with a shared configuration across multiple agents:

**1. Create a shared profile configuration:**

```yaml
# shared-goose-profile.yaml
default:
  provider: anthropic
  processor: claude-sonnet-4-20250514
  accelerator: claude-sonnet-4-20250514
  moderator: passive
  api_key: ${ANTHROPIC_API_KEY}  # Use environment variable

teamwork:
  provider: openrouter
  processor: anthropic/claude-sonnet-4
  api_key: ${OPENROUTER_API_KEY}
```

**2. Deployment script:**

```bash
#!/bin/bash
# deploy-goose-config.sh

# Install Goose if not present
if ! command -v goose &> /dev/null; then
    curl -fsSL https://github.com/block/goose/releases/download/stable/download_cli.sh | bash
fi

# Create config directory
mkdir -p ~/.config/goose

# Download shared configuration
curl -o ~/.config/goose/profiles.yaml https://your-config-server.com/shared-goose-profile.yaml

# Replace environment variables with actual API keys
# (Use TreeTee/MeshCentral environment variable injection)
export ANTHROPIC_API_KEY="your-api-key-here"
envsubst < ~/.config/goose/profiles.yaml > ~/.config/goose/profiles.yaml.tmp
mv ~/.config/goose/profiles.yaml.tmp ~/.config/goose/profiles.yaml

echo "Goose configured successfully"
goose --version
```

**3. Deploy via MeshCentral:**
- Upload `deploy-goose-config.sh` to agents via Files tab
- Run via Terminal: `bash deploy-goose-config.sh`

### Using TreeTee Environment Variables

Store API keys as environment variables on agents:

**Add to agent's shell profile** (`~/.bashrc`, `~/.zshrc`, etc.):
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENROUTER_API_KEY="sk-or-..."
```

Then Goose can reference these in its configuration.

## Security Considerations

### API Key Management

**Never hardcode API keys in scripts committed to Git!**

**Good practices:**
1. **Environment Variables**: Store keys in shell profiles
2. **MeshCentral Secrets**: Use MeshCentral's user data storage
3. **Vault Integration**: Use HashiCorp Vault or similar
4. **Per-Agent Keys**: Different API keys for different machines

### Pre-configured Profile Security

If sharing a Goose configuration file:

```yaml
# profiles.yaml (secure approach)
default:
  provider: anthropic
  processor: claude-sonnet-4-20250514
  accelerator: claude-sonnet-4-20250514
  moderator: passive
  api_key_env: ANTHROPIC_API_KEY  # Reference env var, don't store key directly
```

### Local Model Option (Maximum Privacy)

Use Docker Model Runner for completely private AI:

```bash
# Run local LLM with Docker
docker run -d -p 8000:8000 --name model-runner \
  ghcr.io/docker/model-runner:latest

# Configure Goose to use local model
goose configure
# Select "Custom OpenAI-compatible API"
# API Base URL: http://localhost:8000/v1
# No API key needed
```

## Example Goose Use Cases on TreeTee Agents

### Use Case 1: Debug a Script on Remote Agent

```bash
# Connect to agent via MeshCentral Terminal
goose session start

# In Goose chat:
> "I have a Python script that's failing. Let me show you the error..."
> "Can you help me debug this?"
```

### Use Case 2: Generate Code on Agent

```bash
goose session start

> "Create a FastAPI endpoint that monitors system resources"
> "Add error handling and logging"
> "Write unit tests for this endpoint"
```

### Use Case 3: Automate Agent Configuration

```bash
goose session start

> "Help me write a script to configure nginx as a reverse proxy"
> "Add SSL certificate configuration using Let's Encrypt"
> "Test the configuration and restart nginx"
```

### Use Case 4: Analyze Logs

```bash
goose session start

> "Check /var/log/syslog for errors in the last hour"
> "Summarize what went wrong"
> "Suggest fixes"
```

## Goose Commands Reference

```bash
# Start a chat session
goose session start

# Start with specific profile
goose session start --profile teamwork

# List available profiles
goose configure --list

# Update Goose
goose update

# Check version
goose --version

# View help
goose --help
```

## Troubleshooting

### Goose Not Found After Installation

**Linux/macOS:**
```bash
# Add to PATH
export PATH="$HOME/.local/bin:$PATH"

# Or reload shell
source ~/.bashrc  # or ~/.zshrc
```

**Windows:**
- Restart PowerShell/Terminal
- Check: `$env:Path` includes Goose installation directory

### Configuration Not Saved

**macOS (M3 Macs specific):**
```bash
# Ensure .config directory has write permissions
chmod u+w ~/.config
mkdir -p ~/.config/goose
```

**All platforms:**
```bash
# Verify config file location
ls -la ~/.config/goose/profiles.yaml

# Re-run configuration
goose configure
```

### API Key Issues

```bash
# Test API key manually
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: YOUR_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-sonnet-4-20250514","max_tokens":1024,"messages":[{"role":"user","content":"Hello"}]}'
```

### Goose Session Won't Start

```bash
# Check Goose logs
goose session start --verbose

# Verify configuration
cat ~/.config/goose/profiles.yaml

# Test with different profile
goose session start --profile default
```

## Integration with Ollama (Local LLMs)

If you're using Ollama on your Tailscale network (per CLAUDE.md):

```bash
# Configure Goose to use Ollama on hugo:11434
goose configure

# Provider: Custom OpenAI-compatible API
# API Base URL: http://hugo:11434/v1
# Model: llama3 (or whichever model you have)
# API Key: (leave empty for Ollama)
```

**Tailscale + Ollama + Goose Setup:**

```yaml
# ~/.config/goose/profiles.yaml
local-ollama:
  provider: openai
  processor: llama3
  api_base: http://hugo:11434/v1
  api_key: none
```

Then use: `goose session start --profile local-ollama`

## Deployment Checklist

- [ ] Install Goose on target agents (Linux, macOS, or Windows)
- [ ] Configure with AI provider (Anthropic, OpenAI, OpenRouter, or local)
- [ ] Test Goose session starts successfully
- [ ] (Optional) Create shared configuration profile
- [ ] (Optional) Add custom MeshCentral buttons for quick access
- [ ] (Optional) Set up environment variables for API keys
- [ ] Document which agents have Goose installed
- [ ] Train users on how to access Goose via MeshCentral

## Cost Estimation

### API-based Models

Typical usage (per agent per month):
- **Light use** (1-2 sessions/day): $5-10/month
- **Medium use** (5-10 sessions/day): $20-40/month
- **Heavy use** (constant development): $100+/month

**Cost-saving tips:**
1. Use local models (Ollama) for free compute-only costs
2. Share API keys across team (track usage)
3. Use cheaper models for simple tasks
4. Set usage limits in provider dashboards

### Local Models (Ollama)

- **Cost**: Free (compute only)
- **Trade-off**: Slower, requires GPU, less capable than Claude/GPT-4
- **Best for**: Privacy-sensitive work, cost-conscious deployments

## Resources

- **Goose Documentation**: https://block.github.io/goose/
- **Goose GitHub**: https://github.com/block/goose
- **MeshCentral Docs**: https://ylianst.github.io/MeshCentral/
- **Anthropic API**: https://console.anthropic.com
- **OpenRouter**: https://openrouter.ai
- **Ollama**: https://ollama.ai

## Next Steps

1. **Test installation**: Install Goose on one agent first
2. **Configure with your preferred AI provider**
3. **Create usage guide**: Document for your team
4. **Roll out to more agents**: Use automation scripts
5. **Monitor costs**: Track API usage across agents
6. **Gather feedback**: See how team uses Goose on remote machines

---

**TreeTee + Goose = AI-powered remote development at scale**
