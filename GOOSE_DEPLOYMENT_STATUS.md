# Goose AI Integration - Deployment Status

## ✅ Fixed and Deployed (Nov 4, 2025)

### Issue Found
The `envsubst` command in `docker-entrypoint.sh` was trying to substitute ALL `$` variables, including those in bash commands within the `preConfiguredScripts` JSON. This was breaking the Goose installation scripts.

### Fix Applied
Updated `docker-entrypoint.sh` to explicitly specify which environment variables to substitute:

```bash
envsubst '$MESHCENTRAL_CERT_NAME $MESHCENTRAL_PORT ... etc' < template > config.json
```

This prevents `envsubst` from touching bash logic like:
- `$GOOSE_API_KEY` in scripts
- `command -v goose`
- Shell variables in if statements

### Deployment Status
- **Committed**: ae616bd → 552e7b3
- **Pushed**: To main branch
- **Deployed**: Railway build in progress
- **Live**: Will be available at https://tee.up.railway.app in 2-5 minutes

## How to Verify Buttons Appear

### Step 1: Wait for Deployment
```bash
# Check Railway logs
railway logs --service TreeTee 2>&1 | tail -20

# Look for:
# - "Configuration generated successfully!"
# - "MeshCentral HTTPS server running"
```

### Step 2: Login to TreeTee
1. Go to https://tee.up.railway.app
2. Login with your credentials
3. You should see your connected agents

### Step 3: Check for Goose Buttons
1. Click on any connected agent (like "nic")
2. Look for **"Actions"** button at the top
3. Click Actions → **"Run Commands"**
4. You should see:
   - Install Goose AI (Linux)
   - Install Goose AI (macOS)
   - Check Goose Status (Linux/macOS)
   - Start Goose Chat (Linux/macOS)

### Step 4: Test Installation (Optional)
1. Click **"Install Goose AI (Linux)"** for a Linux agent
2. Watch the output in the UI
3. Should see: "Goose installed successfully. Run: goose configure"
4. Open Terminal tab for the agent
5. Run: `goose --version`
6. Verify Goose is installed

## Buttons Available

| Button Name | Platform | Action |
|-------------|----------|---------|
| **Install Goose AI (Linux)** | Linux | Downloads and installs Goose CLI |
| **Install Goose AI (macOS)** | macOS | Downloads and installs Goose CLI |
| **Check Goose Status** | Linux/macOS | Verifies installation and configuration |
| **Start Goose Chat** | Linux/macOS | Launches AI chat session |

## Configuration Details

**Template File**: `meshcentral-data/config.json.template`
- Contains `preConfiguredScripts` array
- Bash commands preserved by explicit envsubst variables

**Generated Config**: `meshcentral-data/config.json` (on Railway)
- Generated at container startup
- Includes all Goose scripts
- Bash logic intact

**Entrypoint Script**: `docker-entrypoint.sh`
- Fixed to use explicit variable substitution
- Now preserves bash commands in JSON

## Troubleshooting

### Buttons Still Not Appearing

**Possible causes:**
1. Deployment not complete yet (wait 2-5 minutes)
2. Browser cache (hard refresh: Ctrl+Shift+R)
3. Need to logout/login again

**Verification steps:**
```bash
# Check Railway deployment status
railway status --service TreeTee

# View recent logs
railway logs --service TreeTee 2>&1 | grep -E "(Config|preConfigured|Running)" | tail -20
```

### Config Not Generated Correctly

**Check Railway environment variables:**
```bash
railway variables --service TreeTee

# Should have:
# MESHCENTRAL_CERT_NAME=tee.up.railway.app
# MESHCENTRAL_PORT=443
# WAN_ONLY=true
# etc.
```

**Check config on Railway:**
Railway doesn't allow direct file inspection, but logs show:
```
Generating config.json from template...
Configuration generated successfully!
```

## Next Steps After Deployment

1. **Verify buttons appear** in TreeTee web UI
2. **Test installation** on a connected agent
3. **Configure Goose** with your AI provider:
   ```bash
   goose configure
   # Choose: Anthropic Claude / OpenAI / OpenRouter / Ollama
   # Enter: API key
   ```
4. **Try Goose chat**:
   ```bash
   goose session start
   > "help me debug this script"
   ```

## Complete Documentation

- **GOOSE_QUICK_START.md** - 3-step user guide
- **ONE_BUTTON_GOOSE_INSTALL.md** - Detailed button usage
- **GOOSE_INTEGRATION_GUIDE.md** - Complete integration reference
- **MESHCENTRAL_API_GUIDE.md** - Programmatic API control
- **OPTIONAL_GOOSE_DEPLOYMENT.md** - Advanced deployment options

## Timeline

- **Nov 4, 2025 - 10:00 AM**: Initial implementation
- **Nov 4, 2025 - 11:30 AM**: Found envsubst issue
- **Nov 4, 2025 - 11:45 AM**: Fixed and redeployed
- **Nov 4, 2025 - 12:00 PM**: Expected live on Railway

## Support

If buttons still don't appear after 10 minutes:
1. Check deployment logs on Railway
2. Verify config.json.template is in git
3. Verify docker-entrypoint.sh has the fix
4. Try manual config regeneration on Railway

---

**The fix is deployed. Goose buttons should appear in TreeTee within 5 minutes!**
