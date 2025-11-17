# Testing the DaisyChain Proxy API

This guide shows how to test the proxy API locally and on Railway.

## Prerequisites

1. **MeshCentral Login Token**
   - Log into https://tee.up.railway.app
   - Go to "My Account" → "Account Security" → "Login Tokens"
   - Click "Create New Login Token"
   - Copy the token

2. **Set Environment Variables**
   ```bash
   export DAISYCHAIN_URL=tee.up.railway.app
   export DAISYCHAIN_TOKEN=<your-token-from-above>
   export PROXY_API_KEY=test-secret-key-123
   ```

## Test Locally

### 1. Install Dependencies

```bash
cd proxy
pip install -r requirements.txt
```

### 2. Run the Proxy

```bash
# Make sure environment variables are set
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Test Health Endpoint

```bash
# In another terminal
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "meshcentral_url": "https://tee.up.railway.app",
  "authenticated": true,
  "api_version": "2.0.0"
}
```

### 4. Test Root Endpoint

```bash
curl http://localhost:8000/
```

**Expected Response:**
```json
{
  "service": "DaisyChain Proxy API v2",
  "status": "running",
  "authenticated": true,
  "version": "2.0.0",
  "approach": "Hybrid REST+WebSocket"
}
```

### 5. Test Device Listing (Requires API Key)

```bash
curl -H "X-API-Key: test-secret-key-123" \
  http://localhost:8000/api/devices
```

**Expected Response:**
```json
{
  "success": true,
  "devices": {
    ...device data from MeshCentral...
  }
}
```

### 6. Test Info Endpoint

```bash
curl -H "X-API-Key: test-secret-key-123" \
  http://localhost:8000/api/info
```

**Expected Response:**
```json
{
  "meshcentral_url": "https://tee.up.railway.app",
  "authenticated": true,
  "api_version": "2.0.0",
  "features": {
    "device_listing": "REST API",
    "commands": "Pending WebSocket",
    "screenshots": "Pending WebSocket"
  }
}
```

## Test on Railway

### 1. Check Railway Environment Variables

```bash
railway variables
```

Verify these are set:
- `DAISYCHAIN_URL` = tee.up.railway.app
- `DAISYCHAIN_TOKEN` = (your login token)
- `PROXY_API_KEY` = (your API key)

### 2. Deploy to Railway

```bash
# From repository root
railway up
```

### 3. Wait for Deployment

```bash
# Wait 60 seconds
sleep 60

# Check logs
railway logs | tail -30
```

Look for:
```
INFO:app:Starting DaisyChain Proxy v2...
INFO:app:MeshCentral URL: https://tee.up.railway.app
INFO:app:Successfully authenticated with MeshCentral
INFO:app:Proxy ready and authenticated
```

### 4. Test Railway Health Endpoint

```bash
# Get your Railway URL
railway domain

# Test health (example URL)
curl https://your-service.up.railway.app/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "meshcentral_url": "https://tee.up.railway.app",
  "authenticated": true,
  "api_version": "2.0.0"
}
```

### 5. Test Railway API Endpoints

```bash
# Set your Railway URL
export PROXY_URL=https://your-service.up.railway.app
export API_KEY=your-proxy-api-key

# Test device listing
curl -H "X-API-Key: $API_KEY" \
  $PROXY_URL/api/devices

# Test info endpoint
curl -H "X-API-Key: $API_KEY" \
  $PROXY_URL/api/info
```

## Common Issues

### Issue: "Authentication failed: noauth"

**Cause:** Using old WebSocket code instead of new REST API code

**Solution:**
1. Verify `proxy/app.py` contains v2 code (check for "v2" in first lines)
2. Redeploy to Railway: `railway up`
3. Check Railway build logs to ensure new code deployed

### Issue: 502 Bad Gateway

**Causes:**
1. App crashed during startup
2. Authentication failed
3. Port mismatch

**Solutions:**
```bash
# Check logs for errors
railway logs | grep ERROR

# Verify PORT environment variable
railway variables | grep PORT

# Restart service
railway restart
```

### Issue: "Invalid API key" (403 Error)

**Cause:** Wrong API key or header

**Solution:**
```bash
# Check your API key
railway variables | grep PROXY_API_KEY

# Use correct header name
curl -H "X-API-Key: your-key-here" ...
```

### Issue: "DAISYCHAIN_TOKEN not set"

**Cause:** Missing MeshCentral login token

**Solution:**
```bash
# Get token from MeshCentral UI
# Then set in Railway
railway variables set DAISYCHAIN_TOKEN=your-token
```

## Troubleshooting Commands

### Check Which Code Version is Running

```bash
# Local
curl http://localhost:8000/ | grep version

# Railway
curl https://your-service.up.railway.app/ | grep version
```

v1 (old) will show: `"version": "1.0.0"`
v2 (new) will show: `"version": "2.0.0", "approach": "Hybrid REST+WebSocket"`

### View Recent Logs

```bash
# Last 50 lines
railway logs | tail -50

# Follow live logs
railway logs --follow

# Filter for errors
railway logs | grep -i error
```

### Force Redeploy

```bash
# Redeploy current code
railway redeploy

# Or upload and deploy
railway up
```

### Test MeshCentral Direct Access

```bash
# Verify MeshCentral is accessible
curl -I https://tee.up.railway.app/

# Should return 200 OK
```

## Success Criteria

✅ Health endpoint returns `"status": "healthy"`
✅ Version shows `"2.0.0"`
✅ Authenticated shows `true`
✅ Device listing works (with valid API key)
✅ No ERROR messages in logs

## Next Steps After Testing

Once proxy is working:

1. **Add WebSocket for Commands**
   - Implement command execution via WebSocket
   - Add screenshot support

2. **Test with Real Devices**
   - Install MeshAgent on a test machine
   - Try sending commands via proxy API

3. **Deploy to Production**
   - Merge to main branch
   - Update Railway to use `latest` tag instead of `dev`

## Additional Resources

- **Proxy Code:** `proxy/app.py` (v2 with REST API)
- **Original WebSocket:** `proxy/app_v1_websocket.py` (backup)
- **MeshCentral Docs:** https://github.com/Ylianst/MeshCentral
- **Railway Docs:** https://docs.railway.app/
