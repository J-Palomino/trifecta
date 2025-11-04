# One-Button Goose AI Installation from MeshCentral

## Overview

DaisyChain now includes **one-click Goose AI installation buttons** in the MeshCentral web interface. No terminal commands required - just click a button!

## How It Works

Pre-configured scripts appear in the MeshCentral device interface under **Actions** → **Run Commands**. These scripts install and manage Goose AI with a single click.

## Available One-Click Actions

### 1. Install Goose AI (Linux)
- **What it does**: Downloads and installs Goose CLI on Linux agents
- **Platforms**: Ubuntu, Debian, CentOS, RHEL, Fedora, etc.
- **Duration**: 30-60 seconds
- **Requires**: Internet connection

### 2. Install Goose AI (macOS)
- **What it does**: Downloads and installs Goose CLI on macOS agents
- **Platforms**: macOS 10.9+, both Intel and Apple Silicon
- **Duration**: 30-60 seconds
- **Requires**: Internet connection

### 3. Check Goose Status (Linux/macOS)
- **What it does**: Verifies Goose installation and configuration status
- **Shows**: Version, config file location, installation status
- **Duration**: < 5 seconds

### 4. Start Goose Chat (Linux/macOS)
- **What it does**: Launches interactive Goose AI chat session
- **Requires**: Goose must be installed and configured first
- **Use**: For quick AI assistance on the remote machine

## Step-by-Step: First Time Setup

### Step 1: Access Device in DaisyChain

1. Login to DaisyChain at https://tee.up.railway.app
2. Navigate to **My Devices**
3. Click on the device where you want Goose

### Step 2: Run Installation Script

1. Click **Actions** button (or right-click the device)
2. Select **Run Commands**
3. Find **"Install Goose AI (Linux)"** or **"Install Goose AI (macOS)"**
4. Click the script name
5. Confirm execution
6. Wait for "Goose installed successfully" message

### Step 3: Configure Goose (First Time Only)

After installation, you need to configure Goose with an AI provider:

**Option A: Via Terminal**
1. Open **Terminal** for the device in MeshCentral
2. Run: `goose configure`
3. Choose provider (Anthropic, OpenAI, OpenRouter, etc.)
4. Enter API key
5. Select default model

**Option B: Pre-configured Profile (Advanced)**
- Deploy a shared `profiles.yaml` configuration file
- See GOOSE_INTEGRATION_GUIDE.md for details

### Step 4: Verify Installation

1. Click **Actions** → **Run Commands**
2. Select **"Check Goose Status (Linux/macOS)"**
3. Verify output shows:
   - Goose version number
   - "Goose is configured" message

### Step 5: Start Using Goose

**From MeshCentral UI:**
1. Click **Actions** → **Run Commands**
2. Select **"Start Goose Chat (Linux/macOS)"**
3. Goose chat session starts in the terminal

**From Device Terminal:**
1. Open Terminal in MeshCentral
2. Run: `goose session start`
3. Chat with AI directly

## Using the One-Click Buttons

### Where to Find Them

**Method 1: Actions Menu**
1. Click device in DaisyChain
2. Click **"Actions"** button at top
3. Select **"Run Commands"**
4. Choose from Goose scripts

**Method 2: Right-Click Context Menu**
1. Right-click on device in device list
2. Select **"Run Commands"**
3. Choose from Goose scripts

**Method 3: Device Page**
1. Open device details page
2. Find **"Run"** button
3. Right-click for script menu
4. Select Goose action

### Execution Flow

```
Click Button
  ↓
Script Runs on Agent
  ↓
Real-time Output in UI
  ↓
Success/Failure Message
  ↓
Done!
```

## Example Workflow

### Scenario: Installing Goose on a Development Server

```
1. [User] Click "dev-server-01" in DaisyChain
2. [User] Actions → Run Commands → "Install Goose AI (Linux)"
3. [System] Downloads and installs Goose CLI
4. [System] Shows: "Goose installed successfully. Run: goose configure"
5. [User] Opens Terminal tab
6. [User] Runs: goose configure
7. [User] Chooses: Anthropic Claude
8. [User] Enters: API key
9. [System] Goose configured
10. [User] Actions → Run Commands → "Start Goose Chat"
11. [System] Goose chat starts
12. [User] Types: "help me debug this Python script"
13. [Goose] Provides AI assistance
```

## Script Details

### Install Goose AI (Linux/macOS)

```bash
curl -fsSL https://github.com/block/goose/releases/download/stable/download_cli.sh | bash && \
echo 'Goose installed successfully. Run: goose configure'
```

**What happens:**
- Downloads official Goose installer
- Installs to `~/.local/bin/goose`
- Adds to user's PATH
- Shows success message

**Runs as:** User (not root/sudo)
**Non-blocking:** MeshAgent unaffected if fails

### Check Goose Status

```bash
if command -v goose &> /dev/null; then
  goose --version && \
  echo 'Config:' && \
  ls -la ~/.config/goose/profiles.yaml 2>/dev/null && \
  echo 'Goose is configured' || echo 'Run: goose configure'
else
  echo 'Goose not installed'
fi
```

**What it checks:**
- Is Goose command available?
- What version is installed?
- Does config file exist?
- Is Goose ready to use?

### Start Goose Chat

```bash
if command -v goose &> /dev/null; then
  echo 'Starting Goose AI...' && \
  goose session start
else
  echo 'Goose not installed. Run Install Goose AI first.'
fi
```

**What happens:**
- Verifies Goose is installed
- Launches interactive chat session
- Connects to configured AI provider
- Starts chat interface

## Troubleshooting

### Button Doesn't Appear

**Cause:** Config not regenerated after update

**Fix:**
```bash
# On your local machine or deployment server
./generate-config.sh
git add meshcentral-data/config.json
git commit -m "Regenerate config with Goose buttons"
railway up --service DaisyChain
```

### Installation Fails

**Cause 1:** No internet connection on agent

**Fix:** Verify agent can reach github.com:
```bash
ping github.com
```

**Cause 2:** Insufficient permissions

**Fix:** Scripts run as user, should work. Check user has write access to `~/.local/bin`

**Cause 3:** Disk space

**Fix:** Check available space:
```bash
df -h ~
```

### Script Runs But No Output

**Cause:** Script completed too quickly

**Fix:** Run "Check Goose Status" to verify installation

### "Goose not configured" After Install

**Cause:** Need to run `goose configure` first

**Fix:**
1. Open Terminal in MeshCentral
2. Run: `goose configure`
3. Follow prompts to set up AI provider

### Start Goose Chat Does Nothing

**Cause:** Goose not configured or API key invalid

**Fix:**
1. Run "Check Goose Status" button
2. Verify configuration exists
3. Test API key manually:
   ```bash
   goose session start
   ```
4. Check error messages

## Adding More Scripts

You can add custom scripts by editing `meshcentral-data/config.json.template`:

```json
{
  "domains": {
    "": {
      "preConfiguredScripts": [
        {
          "name": "Your Custom Script Name",
          "cmd": "your-command-here",
          "type": "sh",
          "runas": "user"
        }
      ]
    }
  }
}
```

**Example: Update Goose**
```json
{
  "name": "Update Goose AI",
  "cmd": "goose update && goose --version",
  "type": "sh",
  "runas": "user"
}
```

**Example: Configure Goose with Ollama**
```json
{
  "name": "Configure Goose for Ollama",
  "cmd": "mkdir -p ~/.config/goose && cat > ~/.config/goose/profiles.yaml <<'EOF'\ndefault:\n  provider: openai\n  api_base: http://hugo:11434/v1\n  processor: llama3\n  api_key: none\nEOF\n&& echo 'Goose configured for Ollama on hugo:11434'",
  "type": "sh",
  "runas": "user"
}
```

After adding scripts:
1. Regenerate config: `./generate-config.sh`
2. Deploy to Railway: `railway up`
3. Buttons appear in MeshCentral UI

## Security Considerations

### Script Execution

- Scripts run as the **user**, not root
- Cannot modify system files
- Limited to user's permissions
- Safe for multi-user systems

### API Keys

- Never hardcode API keys in scripts
- Use `goose configure` interactively
- Or deploy pre-configured profiles securely
- Consider environment variables

### Network Access

- Scripts download from github.com
- Ensure agents have internet access
- Firewall may need github.com whitelisted
- HTTPS (port 443) must be allowed

## Best Practices

1. **Test on one agent first** before bulk deployment
2. **Verify agent connectivity** before installing Goose
3. **Document which agents have Goose** installed
4. **Monitor API usage** to track costs
5. **Use shared configurations** for consistency
6. **Keep scripts updated** in config template

## Deployment Workflow

```
1. Update config.json.template with new scripts
2. Run: ./generate-config.sh
3. Commit: git add meshcentral-data/config.json.template
4. Deploy: railway up --service DaisyChain
5. Wait for deployment
6. Login to DaisyChain
7. Navigate to device
8. Click Actions → Run Commands
9. See new buttons!
```

## Quick Reference

| Action | Purpose | Duration | Requirements |
|--------|---------|----------|--------------|
| Install Goose AI (Linux) | Install Goose CLI | 30-60s | Internet |
| Install Goose AI (macOS) | Install Goose CLI | 30-60s | Internet |
| Check Goose Status | Verify installation | < 5s | None |
| Start Goose Chat | Launch AI chat | < 5s | Goose configured |

## Next Steps

1. **Deploy config update** to Railway
2. **Test installation** on one agent
3. **Configure Goose** with your AI provider
4. **Roll out** to more agents as needed
5. **Train users** on how to access Goose

## Resources

- **Goose Documentation**: https://block.github.io/goose/
- **MeshCentral Scripts**: https://ylianst.github.io/MeshCentral/meshcentral/config/
- **DaisyChain Goose Guide**: GOOSE_INTEGRATION_GUIDE.md
- **Optional Deployment**: OPTIONAL_GOOSE_DEPLOYMENT.md

---

**One button. That's all it takes to add AI chat to your remote machines.**
