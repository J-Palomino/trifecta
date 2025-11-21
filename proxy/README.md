# DaisyChain Proxy API

**Standalone REST API service for MeshCentral remote device control**

This service provides HTTP REST API endpoints that connect to any MeshCentral server via WebSocket and expose device control capabilities. Deploy this service completely independently from your MeshCentral infrastructure.

## What This Service Does

The Proxy API acts as a WebSocket-to-REST bridge:

1. Maintains a persistent WebSocket connection to a remote MeshCentral server
2. Authenticates using a MeshCentral login token
3. Exposes REST API endpoints for:
   - Sending shell commands to connected devices
   - Capturing screenshots from connected devices
   - Listing all connected devices
4. Routes HTTP requests to WebSocket messages and back

## Architecture

```
┌─────────────────┐         WebSocket          ┌──────────────────┐
│                 │◄──────────────────────────►│                  │
│  Proxy API      │  wss://meshcentral.com     │  MeshCentral     │
│  (This Service) │    /control.ashx           │  Server          │
│                 │                             │  (Remote)        │
└────────┬────────┘                             └────────┬─────────┘
         │                                               │
         │ REST API                                      │ Manages
         ▼                                               ▼
   ┌─────────┐                                    ┌──────────────┐
   │  Your   │                                    │   Devices    │
   │  Client │                                    │   (Agents)   │
   │  Apps   │                                    └──────────────┘
   └─────────┘
```

## Quick Start

### Deploy to Railway

1. **Create New Service in Railway:**
   ```
   Railway Dashboard → New → Empty Service
   ```

2. **Set Root Directory:**
   ```
   Settings → Service → Root Directory: /proxy
   ```

3. **Set Environment Variables:**
   ```
   DAISYCHAIN_URL=your-meshcentral-server.com
   DAISYCHAIN_TOKEN=<your-login-token>
   PROXY_API_KEY=<generate-a-secure-key>
   ```

4. **Deploy:**
   ```bash
   # From repository root
   git push origin main
   ```

   Railway will:
   - Detect `proxy/Dockerfile`
   - Build the container
   - Deploy on assigned `$PORT`
   - Expose at `https://your-proxy.up.railway.app`

### Local Development

```bash
cd proxy
pip install -r requirements.txt

# Set environment variables
export DAISYCHAIN_URL=tee.up.railway.app
export DAISYCHAIN_TOKEN=your-token
export PROXY_API_KEY=test-key

# Run with hot reload
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### Docker Deployment

```bash
# Build
cd proxy
docker build -t daisychain-proxy:latest .

# Run
docker run -d \
  -p 8000:8000 \
  -e DAISYCHAIN_URL=tee.up.railway.app \
  -e DAISYCHAIN_TOKEN=your-token \
  -e PROXY_API_KEY=your-api-key \
  --name daisychain-proxy \
  daisychain-proxy:latest
```

## Configuration

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DAISYCHAIN_URL` | MeshCentral server URL (without protocol) | `tee.up.railway.app` |
| `DAISYCHAIN_TOKEN` | MeshCentral login token for authentication | `abc123...` |
| `PROXY_API_KEY` | API key for securing proxy endpoints | `secure-random-key` |
| `PORT` | HTTP port (auto-provided by Railway) | `8000` |

### Getting MeshCentral Token

1. Log into your MeshCentral web interface
2. Click your username → "My Account"
3. Scroll to "Account Security" → "Login Tokens"
4. Click "Create New Login Token"
5. Copy the token and set as `DAISYCHAIN_TOKEN`

## API Endpoints

### Health Check

```bash
GET /health

# Response
{
  "status": "healthy",
  "meshcentral_connected": true,
  "meshcentral_url": "tee.up.railway.app"
}
```

### Send Command to Device

```bash
POST /api/command
Headers:
  X-API-Key: your-proxy-api-key
  Content-Type: application/json

Body:
{
  "device_id": "node//ABC123...",
  "command": "ls -la /home",
  "timeout": 30
}

# Response
{
  "success": true,
  "device_id": "node//ABC123...",
  "command": "ls -la /home",
  "result": {
    "output": "total 48\ndrwxr-xr-x...",
    "exit_code": 0
  }
}
```

### Get Screenshot from Device

```bash
POST /api/screenshot
Headers:
  X-API-Key: your-proxy-api-key
  Content-Type: application/json

Body:
{
  "device_id": "node//ABC123...",
  "timeout": 30
}

# Response
{
  "success": true,
  "device_id": "node//ABC123...",
  "screenshot": "iVBORw0KGgoAAAANSUhEUgAA...",  # Base64 encoded PNG
  "format": "png"
}
```

### List Connected Devices

```bash
GET /api/devices
Headers:
  X-API-Key: your-proxy-api-key

# Response
{
  "success": true,
  "devices": {
    "node//ABC123...": {
      "name": "My Computer",
      "online": true,
      "platform": "linux"
    },
    ...
  }
}
```

## Security

### API Key Authentication

All API endpoints (except `/health` and `/`) require the `X-API-Key` header:

```bash
curl -H "X-API-Key: your-api-key" https://your-proxy.railway.app/api/devices
```

### Best Practices

1. **Generate Strong API Keys:**
   ```bash
   openssl rand -hex 32
   ```

2. **Use HTTPS Only:**
   - Railway provides automatic HTTPS
   - Never expose over plain HTTP in production

3. **Rotate Tokens Regularly:**
   - Regenerate `DAISYCHAIN_TOKEN` monthly
   - Regenerate `PROXY_API_KEY` when compromised

4. **Network Isolation:**
   - Deploy proxy in private network if possible
   - Use Railway's private networking for service-to-service communication

5. **Monitor Access:**
   ```bash
   railway logs --service proxy | grep "X-API-Key"
   ```

## Monitoring

### Health Check

Railway automatically monitors `/health` endpoint every 30 seconds.

### Logs

```bash
# Real-time logs
railway logs --service proxy --follow

# Check connection status
railway logs --service proxy | grep "Connected to MeshCentral"

# Check for errors
railway logs --service proxy | grep -i "error"
```

### Metrics

The proxy exposes connection metrics:

```python
GET /api/info

{
  "daisychain_url": "tee.up.railway.app",
  "connected": true,
  "api_version": "1.0.0"
}
```

## Troubleshooting

### Proxy Won't Connect to MeshCentral

**Symptoms:** Logs show "Connection failed" or "Authentication failed"

**Solutions:**
1. Verify `DAISYCHAIN_URL` doesn't include `https://` or `/` at the end
2. Regenerate MeshCentral login token
3. Check MeshCentral server is accessible:
   ```bash
   curl https://your-meshcentral-server.com
   ```

### WebSocket Connection Dropped

**Symptoms:** Logs show "WebSocket connection closed"

**Solutions:**
1. Check MeshCentral server logs for errors
2. Verify token hasn't expired
3. Railway will auto-restart on failure (max 10 retries)

### API Returns 403 Forbidden

**Symptoms:** `{"detail": "Invalid API key"}`

**Solutions:**
1. Verify `X-API-Key` header is set correctly
2. Check `PROXY_API_KEY` environment variable matches
3. Restart service after changing variables:
   ```bash
   railway restart --service proxy
   ```

### Timeout Errors

**Symptoms:** `{"detail": "No response from device after 30s"}`

**Solutions:**
1. Increase timeout in request body
2. Check device is online in MeshCentral
3. Verify device has MeshAgent installed and running

## Development

### Project Structure

```
proxy/
  ├── app.py              # FastAPI application
  ├── Dockerfile          # Container definition
  ├── railway.json        # Railway deployment config
  ├── requirements.txt    # Python dependencies
  └── README.md          # This file
```

### Adding New Endpoints

Edit `app.py`:

```python
@app.post("/api/your-endpoint")
async def your_endpoint(
    req: YourRequest,
    api_key: str = Depends(verify_api_key)
):
    # Your implementation
    result = meshcentral.your_method(req.data)
    return {"success": True, "result": result}
```

### Testing

```bash
# Install test dependencies
pip install pytest httpx

# Run tests
pytest test_proxy.py

# Test with curl
../test-proxy.sh
```

## License

MIT - See LICENSE file in repository root
