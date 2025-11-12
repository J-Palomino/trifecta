# DaisyChain Proxy Deployment Guide

## Railway Dashboard Setup (Required)

The Railway CLI has limitations for linking GitHub repos to services, so complete these steps in the Railway web dashboard:

### Step 1: Access Your Project
1. Go to https://railway.app/dashboard
2. Navigate to your "TreeTee" project

### Step 2: Add New Service
1. Click the "+ New" button in your project
2. Select "GitHub Repo"
3. Choose repository: `J-Palomino/trifecta`
4. Select branch: `dev`
5. Name the service: `DaisyChain-Proxy`

### Step 3: Configure Build Settings
1. Click on the new "DaisyChain-Proxy" service
2. Go to "Settings" tab
3. Scroll to "Build" section:
   - **Root Directory**: `proxy`
   - **Builder**: Dockerfile (should auto-detect)
   - Railway will use `proxy/railway.json` configuration automatically

### Step 4: Set Environment Variables
1. Go to "Variables" tab in the DaisyChain-Proxy service
2. Click "New Variable" and add these three variables:

```
DAISYCHAIN_URL=tee.up.railway.app
PROXY_API_KEY=387c7f2ef300cc48823b65da982ef77179d8cb18bbdc5acd1a237adc84f39cf4
DAISYCHAIN_TOKEN=<you_need_to_get_this>
```

### Step 5: Get DAISYCHAIN_TOKEN
1. Go to https://tee.up.railway.app in your browser
2. Log in with user: `juan` / your password
3. Click your username in top right corner
4. Select "My Account"
5. Scroll to "Account Security" section
6. Under "Login Tokens", click "Add Login Token"
7. Name it: `proxy-service`
8. Click "Create Token"
9. Copy the generated token
10. Go back to Railway dashboard
11. Add/update the `DAISYCHAIN_TOKEN` variable with the copied token

### Step 6: Deploy
1. After all variables are set, Railway will automatically trigger a deployment
2. Monitor progress in the "Deployments" tab
3. Wait for build to complete and health check to pass

### Step 7: Generate Public Domain
1. Once deployed, go to "Settings" tab
2. Scroll to "Networking" section
3. Click "Generate Domain"
4. Railway will provide a URL like: `https://daisychain-proxy-production-xxxx.up.railway.app`

### Step 8: Test the Deployment

Once you have the public URL, test it:

```bash
# Health check
curl https://your-proxy-url.railway.app/health

# Expected response:
# {"status":"healthy","meshcentral_connected":true,"meshcentral_url":"tee.up.railway.app"}
```

You can also visit the API documentation at:
```
https://your-proxy-url.railway.app/docs
```

## API Usage

Once deployed, you can use the proxy API from any Python script:

```python
import requests

API_URL = "https://your-proxy-url.railway.app"
API_KEY = "387c7f2ef300cc48823b65da982ef77179d8cb18bbdc5acd1a237adc84f39cf4"

headers = {"X-API-Key": API_KEY}

# List devices
response = requests.get(f"{API_URL}/api/devices", headers=headers)
print(response.json())

# Send command
response = requests.post(
    f"{API_URL}/api/command",
    json={
        "device_id": "node//your_device_id",
        "command": "whoami"
    },
    headers=headers
)
print(response.json())

# Get screenshot
response = requests.post(
    f"{API_URL}/api/screenshot",
    json={"device_id": "node//your_device_id"},
    headers=headers
)

# Save screenshot
import base64
screenshot_b64 = response.json()["screenshot"]
with open("screenshot.png", "wb") as f:
    f.write(base64.b64decode(screenshot_b64))
```

## Security Notes

- The `PROXY_API_KEY` above has been generated for you: `387c7f2ef300cc48823b65da982ef77179d8cb18bbdc5acd1a237adc84f39cf4`
- Keep this key secure - anyone with this key can send commands to your devices
- You can regenerate a new key anytime with: `openssl rand -hex 32`
- The `DAISYCHAIN_TOKEN` is a MeshCentral login token - keep it secret
- Both should be stored in Railway environment variables, never hardcoded

## Troubleshooting

If the deployment fails:

1. Check deployment logs in Railway dashboard
2. Verify all environment variables are set correctly
3. Ensure `DAISYCHAIN_TOKEN` is a valid login token from MeshCentral
4. Check that `DAISYCHAIN_URL` matches your MeshCentral instance URL (no https://)

Common issues:
- "Not connected to MeshCentral" → Check DAISYCHAIN_TOKEN is valid
- "Invalid API key" → Verify PROXY_API_KEY matches in your requests
- Health check timeout → Ensure MeshCentral server is accessible from Railway
