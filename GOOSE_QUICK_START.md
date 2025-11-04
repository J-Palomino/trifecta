# Goose AI Quick Start Guide for TreeTee

## What You Just Got

TreeTee now has **one-click AI chat buttons** in the web interface! Install Goose AI assistant on any connected agent with a single click.

## How to Use (3 Easy Steps)

### Step 1: Open TreeTee
Go to https://tee.up.railway.app and login

### Step 2: Click the Button
1. Select a connected device
2. Click **Actions** → **Run Commands**
3. Click **"Install Goose AI (Linux)"** or **"Install Goose AI (macOS)"**
4. Wait 30-60 seconds
5. Done! Goose is installed

### Step 3: Configure & Chat
```bash
# Open Terminal for the device
goose configure
# Choose: Anthropic (or OpenAI, OpenRouter, etc.)
# Enter: Your API key
# Done!

# Start chatting
goose session start
```

## Available Buttons

| Button Name | What It Does | When to Use |
|-------------|--------------|-------------|
| **Install Goose AI (Linux)** | Installs Goose on Linux agents | First time setup |
| **Install Goose AI (macOS)** | Installs Goose on macOS agents | First time setup |
| **Check Goose Status** | Verifies installation | Troubleshooting |
| **Start Goose Chat** | Launches AI chat session | After configuration |

## Example Use Case

```
Scenario: You want AI help debugging a script on a remote server

1. Login to TreeTee
2. Click on "dev-server-01"
3. Actions → Run Commands → "Install Goose AI (Linux)"
4. Wait for "installed successfully" message
5. Open Terminal tab
6. Run: goose configure
7. Choose provider, enter API key
8. Run: goose session start
9. Type: "help me debug this Python script"
10. Get AI assistance directly on the remote machine!
```

## What AI Providers Can I Use?

- **Anthropic Claude** (recommended, best performance)
- **OpenAI GPT-4** (widely available)
- **OpenRouter** (multiple models, easy setup)
- **Ollama (Local)** (free, works with hugo:11434 on Tailscale)
- **Tetrate** ($10 free credits)

## Cost Estimate

- **Light use**: $5-10/month per agent
- **Medium use**: $20-40/month per agent
- **Local (Ollama)**: Free (just compute costs)

## Complete Documentation

- **ONE_BUTTON_GOOSE_INSTALL.md** - Detailed button usage guide
- **GOOSE_INTEGRATION_GUIDE.md** - Complete integration reference
- **OPTIONAL_GOOSE_DEPLOYMENT.md** - Advanced deployment options

## FAQ

**Q: Will this affect my MeshCentral agent?**
A: No! Goose is completely separate and optional. If installation fails, your agent is unaffected.

**Q: Do I need to install Goose on every agent?**
A: No, only install on agents where you want AI assistance.

**Q: Can I use my Ollama server?**
A: Yes! Configure Goose with: `http://hugo:11434/v1` (from CLAUDE.md Tailscale setup)

**Q: What if the button doesn't work?**
A: Check ONE_BUTTON_GOOSE_INSTALL.md for troubleshooting steps.

**Q: How do I get an API key?**
- Anthropic: https://console.anthropic.com
- OpenAI: https://platform.openai.com
- OpenRouter: https://openrouter.ai

## Next Steps

1. ✅ Buttons are now in TreeTee (just deployed!)
2. Pick an agent to test on
3. Click "Install Goose AI"
4. Configure with your API key
5. Start chatting!

---

**One click. That's all you need to add AI chat to your remote machines.**
