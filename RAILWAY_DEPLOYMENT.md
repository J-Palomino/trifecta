# Railway Deployment Guide

This guide explains how to deploy DaisyChain services to Railway using containerized images.

## Architecture Overview

DaisyChain uses a multi-service architecture with two independent Railway deployments:

1. **MeshCentral Service** - Core remote device management server
2. **Proxy Service** - FastAPI REST API bridge to MeshCentral WebSocket

Both services are containerized and can be deployed to Railway using Dockerfiles.

## Prerequisites

- Railway CLI installed: `npm install -g @railway/cli`
- Railway account with project created
- MongoDB instance (Railway provides this)

## Service Configuration

### MeshCentral Service

**Files:**
- `Dockerfile` - Node.js 18 with Python utilities and MongoDB tools
- `railway.json` - Railway deployment configuration
- `docker-entrypoint.sh` - Generates config from environment variables
- `meshcentral-data/config.json.template` - Configuration template

**Railway Configuration (`railway.json`):**
```json
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

**Required Environment Variables:**
- `HOSTNAME` - Your deployment domain (e.g., `tee.up.railway.app`)
- `LETSENCRYPT_EMAIL` - Email for SSL certificate registration
- `MESHCENTRAL_CERT_NAME` - Certificate name (defaults to HOSTNAME)
- `MESHCENTRAL_PORT` - HTTPS port (default: 443)
- `ALLOW_NEW_ACCOUNTS` - Enable user registration (default: false)
- `LETSENCRYPT_PRODUCTION` - Use production Let's Encrypt (default: false)

**Auto-provided by Railway:**
- `MONGO_URL` - MongoDB connection string (from Railway MongoDB service)
- `MONGO_DATABASE` - MongoDB database name

### Proxy Service

**Files:**
- `proxy/Dockerfile` - Python 3.11 with FastAPI
- `proxy/railway.json` - Proxy-specific Railway configuration
- `proxy/app.py` - FastAPI application
- `proxy/requirements.txt` - Python dependencies

**Railway Configuration (`proxy/railway.json`):**
```json
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "proxy/Dockerfile",
    "watchPatterns": ["proxy/**"]
  },
  "deploy": {
    "startCommand": "uvicorn app:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

**Required Environment Variables:**
- `DAISYCHAIN_URL` - MeshCentral server URL (e.g., `tee.up.railway.app`)
- `DAISYCHAIN_TOKEN` - MeshCentral authentication token
- `PROXY_API_KEY` - API key for proxy authentication

**Auto-provided by Railway:**
- `PORT` - Railway assigns this dynamically

## Deployment Steps

### Option 1: Railway Dashboard (Recommended for First Deploy)

#### MeshCentral Service

1. **Create New Service:**
   ```
   Railway Dashboard → New Project → Deploy from GitHub
   ```

2. **Configure Service:**
   - Select repository: `trifecta`
   - Root directory: `/` (uses root `railway.json`)
   - Railway will detect `Dockerfile` automatically

3. **Add MongoDB:**
   ```
   New Service → Database → MongoDB
   ```
   Railway automatically sets `MONGO_URL` and `MONGO_DATABASE`

4. **Set Environment Variables:**
   ```
   Variables Tab → Add Variables:
   HOSTNAME=your-domain.up.railway.app
   LETSENCRYPT_EMAIL=your-email@example.com
   LETSENCRYPT_PRODUCTION=true
   ALLOW_NEW_ACCOUNTS=false
   ```

5. **Deploy:**
   Railway automatically builds and deploys when you push to GitHub

#### Proxy Service

1. **Create New Service:**
   ```
   Railway Dashboard → Add Service → Deploy from GitHub
   ```

2. **Configure Service:**
   - Select repository: `trifecta`
   - Root directory: `/` (uses `proxy/railway.json`)
   - Railway detects `proxy/Dockerfile` from railway.json config

3. **Set Environment Variables:**
   ```
   Variables Tab → Add Variables:
   DAISYCHAIN_URL=your-meshcentral-service.up.railway.app
   DAISYCHAIN_TOKEN=<get-from-meshcentral>
   PROXY_API_KEY=<generate-secure-key>
   ```

4. **Deploy:**
   Pushes to `proxy/**` files trigger automatic redeploy

### Option 2: Railway CLI

#### Initial Setup

```bash
# Login to Railway
railway login

# Link to your project
cd /path/to/trifecta
railway link
```

#### Deploy MeshCentral Service

```bash
# Set environment variables
railway variables set HOSTNAME=tee.up.railway.app
railway variables set LETSENCRYPT_EMAIL=your-email@example.com
railway variables set LETSENCRYPT_PRODUCTION=true

# Deploy (Railway uses root railway.json)
railway up
```

#### Deploy Proxy Service

```bash
# Create a new service for proxy (in Railway dashboard)
# Then link to it
railway link

# Set environment variables
railway variables set DAISYCHAIN_URL=tee.up.railway.app
railway variables set DAISYCHAIN_TOKEN=your-token
railway variables set PROXY_API_KEY=your-api-key

# Deploy from proxy directory
# Railway uses proxy/railway.json automatically
railway up
```

### Option 3: GitHub Actions (CI/CD)

Create `.github/workflows/deploy-railway.yml`:

```yaml
name: Deploy to Railway

on:
  push:
    branches: [main]
    paths:
      - '**'
      - '!proxy/**'  # Separate workflow for proxy

jobs:
  deploy-meshcentral:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install Railway CLI
        run: npm install -g @railway/cli

      - name: Deploy to Railway
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
        run: railway up --service meshcentral
```

Create `.github/workflows/deploy-proxy.yml`:

```yaml
name: Deploy Proxy to Railway

on:
  push:
    branches: [main]
    paths:
      - 'proxy/**'

jobs:
  deploy-proxy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install Railway CLI
        run: npm install -g @railway/cli

      - name: Deploy to Railway
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
        run: railway up --service proxy
```

## Checking Deployment Status

### Via Railway Dashboard

1. Navigate to your project
2. Click on service (MeshCentral or Proxy)
3. View "Deployments" tab for build logs
4. View "Metrics" tab for runtime health

### Via Railway CLI

```bash
# View service logs
railway logs

# Follow logs in real-time
railway logs --follow

# Check deployment status
railway status
```

### Deployment Success Indicators

**MeshCentral:**
- Logs show: "MeshCentral v1.1.42 running"
- Logs show: "Server listening on port 443"
- Health check passes after ~300 seconds

**Proxy:**
- Logs show: "Connected to MeshCentral successfully"
- Health endpoint returns: `{"status": "healthy", "meshcentral_connected": true}`
- Responds within 100 seconds

## Troubleshooting

### MeshCentral Won't Start

1. **Check MongoDB connection:**
   ```bash
   railway logs | grep -i "mongo"
   ```
   Verify `MONGO_URL` is set correctly

2. **Check config generation:**
   ```bash
   railway logs | grep -i "config"
   ```
   Look for "Configuration generated successfully!"

3. **Increase healthcheck timeout:**
   MeshCentral needs time to initialize. Timeout is set to 300s in railway.json

### Proxy Can't Connect to MeshCentral

1. **Verify DAISYCHAIN_URL:**
   Should be the Railway-assigned domain of MeshCentral service

2. **Check authentication token:**
   ```bash
   railway logs --service proxy | grep -i "auth"
   ```

3. **Verify MeshCentral is running:**
   ```bash
   curl https://your-meshcentral.up.railway.app
   ```

### Environment Variables Not Working

1. **Check variable names match:**
   ```bash
   railway variables
   ```

2. **Restart service after setting variables:**
   ```bash
   railway restart
   ```

## Railway-Specific Features

### Watch Patterns

The proxy service uses watch patterns to only redeploy when proxy code changes:

```json
"watchPatterns": ["proxy/**"]
```

This prevents unnecessary redeployments when you modify MeshCentral code.

### Health Checks

Railway monitors these endpoints:
- **Proxy:** `GET /health` (100s timeout)
- **MeshCentral:** No explicit healthcheck path (relies on container staying up, 300s timeout)

### Port Assignment

Railway assigns `$PORT` dynamically. Both services handle this:
- **Proxy:** Uses `${PORT:-8000}` in CMD
- **MeshCentral:** Uses hardcoded 443/80 (Railway maps externally)

## Cost Optimization

### Resource Limits

Set appropriate limits in Railway dashboard:
- **MeshCentral:** 1-2 GB RAM, 1 vCPU
- **Proxy:** 512 MB RAM, 0.5 vCPU

### Sleep Mode

For development environments:
- Enable Railway's sleep mode for inactive services
- Services wake up on first request

## Security Best Practices

1. **Never commit secrets:**
   - Use Railway environment variables
   - Store tokens in Railway dashboard

2. **Use GitHub Secrets for CI/CD:**
   ```
   RAILWAY_TOKEN=<from Railway dashboard>
   ```

3. **Enable HTTPS only:**
   - Railway provides automatic HTTPS
   - Set `LETSENCRYPT_PRODUCTION=true`

4. **Restrict API access:**
   - Set strong `PROXY_API_KEY`
   - Use Railway's built-in authentication

## Monitoring

### Railway Observability

- **Metrics:** CPU, Memory, Network usage in dashboard
- **Logs:** Real-time log streaming
- **Alerts:** Configure webhook notifications for failures

### Custom Monitoring

Add monitoring endpoints to proxy service:
```python
@app.get("/metrics")
async def metrics():
    return {
        "uptime": get_uptime(),
        "requests": request_count,
        "meshcentral_connected": meshcentral.connected
    }
```

## Updating Services

### Rolling Updates

Railway performs zero-downtime deployments:
1. Builds new container
2. Starts new container
3. Health check passes
4. Routes traffic to new container
5. Stops old container

### Manual Deployments

```bash
# Redeploy without code changes
railway redeploy

# Redeploy specific service
railway redeploy --service proxy
```

## Additional Resources

- [Railway Documentation](https://docs.railway.app/)
- [Railway CLI Reference](https://docs.railway.app/develop/cli)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [MeshCentral Documentation](https://ylianst.github.io/MeshCentral/)
