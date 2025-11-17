# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DaisyChain is an AI agent monitoring and control platform that bridges AI agents, virtual machines, and human control. It enables AI agents to control computers via VNC/RDP while providing secure monitoring in Trusted Execution Environments (TEEs).

**Core Services:**
1. **MeshCentral Service**: Remote device management server (npm package v1.1.42) launched via Node.js process spawner (index.js)
2. **Proxy API Service** (`proxy/`): Standalone FastAPI REST API that connects remotely to MeshCentral via WebSocket and exposes device control endpoints
3. **Python Utilities**: Certificate validation and configuration checking tools
4. **Marlin Component**: Separate deployment configuration for the Computer Use Agent (CUA) VM

**Deployment Architecture:**
- **Independent Services**: Proxy API and MeshCentral deploy separately and communicate via WebSocket
- **Proxy API**: Completely standalone - can deploy to any platform and connect to any MeshCentral server
- **MeshCentral**: Docker containerized with two-tier configuration (base + production overlay)
- **Configuration**: Template-based system using environment variable substitution

## Development Commands

### MeshCentral Service

```bash
# Development deployment
docker-compose up -d

# Production deployment (restricted volume mounts)
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild containers
docker-compose build --no-cache

# Generate config.json from environment variables and template
./generate-config.sh

# Verify Docker compose configuration
docker-compose config
```

### Proxy API Service (Standalone)

**Important:** This service is completely independent from MeshCentral infrastructure. It connects to MeshCentral remotely via WebSocket.

```bash
# Local development (from proxy/ directory)
cd proxy
pip install -r requirements.txt

# Set environment variables
export DAISYCHAIN_URL=your-meshcentral-server.com
export DAISYCHAIN_TOKEN=your-login-token
export PROXY_API_KEY=your-api-key

# Run with hot reload
uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# Test proxy endpoints
../test-proxy.sh

# Deploy to Railway
# 1. Create new service with root directory: /proxy
# 2. Set environment variables in Railway dashboard
# 3. Railway will use proxy/railway.json and proxy/Dockerfile
# 4. Proxy connects to remote MeshCentral via wss://DAISYCHAIN_URL/control.ashx
```

### Marlin (Computer Use Agent)

```bash
# Deploy CUA VM locally
docker-compose -f marlin/docker-compose-marlin.yml up -d

# Using pre-built image
docker pull ghcr.io/j-palomino/openai-cua-sample-app:latest
```

### Testing and Validation

```bash
# Check SSL certificates
python3 check_cert.py

# Verify nginx configuration
python3 check_nginx.py

# Test redirects
python3 check_redirects.py

# Audit npm dependencies
npm audit --audit-level=high
```

### Security

Install the security pre-commit hook to prevent committing secrets:
```bash
cp .github/pre-commit-hook.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## Architecture

### Configuration System

DaisyChain uses a two-stage configuration approach:

1. **Template-based generation**: `meshcentral-data/config.json.template` contains MeshCentral config with environment variable placeholders
2. **Environment substitution**: `generate-config.sh` or `docker-entrypoint.sh` uses `envsubst` to replace placeholders with actual values from `.env`
3. **Runtime**: Generated `config.json` is used by MeshCentral at startup

Key environment variables:
- `HOSTNAME`: Deployment domain (required)
- `LETSENCRYPT_EMAIL`: Email for SSL certificate registration (required)
- `NODE_ENV`: Environment mode (production/development)
- `MESHCENTRAL_PORT`: HTTPS port (default: 443)
- `ALLOW_NEW_ACCOUNTS`: Enable/disable user registration (default: false)
- `LETSENCRYPT_PRODUCTION`: Use production Let's Encrypt certs (default: false for local dev)

### Deployment Architecture

**Container Layers:**
1. **Dockerfile**: Node 18-slim base with Python 3 utilities
2. **docker-compose.yml**: Base configuration with full repository mount for development
3. **docker-compose.prod.yml**: Production overlay that restricts volumes to only necessary files (read-only where possible)
4. **docker-entrypoint.sh**: Entrypoint script that generates config and starts MeshCentral

**Process Flow:**
1. Container starts → `docker-entrypoint.sh` runs
2. Script sets default environment variables
3. Runs `envsubst` on config template to generate `config.json`
4. Executes `node ./node_modules/meshcentral` to start server

### Security Model

This repository enforces strict security practices through multiple layers:

**Pre-commit Protection:**
- Git hook scans for `.env` files, certificates (`.pem`, `.key`, `.crt`), private keys
- Pattern matching for hardcoded secrets in staged content
- Interactive warnings for potential sensitive data

**CI/CD Security Scans:**
- TruffleHog: Secret detection in git history
- npm audit: Dependency vulnerability scanning
- CodeQL: Static code analysis for JavaScript and Python
- File scanner: Checks for committed certificates and `.env` files

**Secrets Management:**
- All sensitive data via environment variables (never hardcoded)
- Certificates stored outside repository or auto-generated by Let's Encrypt
- GitHub Secrets for CI/CD pipelines
- `.env` file never committed (template `.env.example` provided)

### Service Communication Flow

**Proxy API Service Architecture (Independent Deployment):**

The `proxy/` service is a standalone API that connects remotely to MeshCentral:

```
Client Apps → REST API → Proxy Service → WebSocket → MeshCentral Server → Devices
              (HTTPS)    (Independent)   (WSS)       (Remote Server)
```

Key features:
1. **Independent Deployment**: Deploy anywhere (Railway, AWS, GCP, etc.) - no need to be co-located with MeshCentral
2. **Remote Connection**: Connects to MeshCentral via WebSocket (`wss://{DAISYCHAIN_URL}/control.ashx`)
3. **Token Authentication**: Uses MeshCentral login token (`DAISYCHAIN_TOKEN`) for authentication
4. **REST API Endpoints**:
   - `POST /api/command` - Send shell commands to any connected device/agent
   - `POST /api/screenshot` - Request screenshots from any connected device/agent
   - `GET /api/devices` - List all devices connected to MeshCentral
5. **Request-Response Queuing**: Tags WebSocket messages to route responses back to correct HTTP requests
6. **Thread-Safe**: Background listener thread handles WebSocket messages while FastAPI serves HTTP requests
7. **API Key Security**: All endpoints require `X-API-Key` header (except `/health`)

**Configuration Template System:**
The config generation uses a multi-layer approach to support both local development and Railway deployment:
- `config.json.template`: Contains MeshCentral configuration with `${VAR}` placeholders
- `docker-entrypoint.sh`: Sets defaults, runs `envsubst` to generate `config.json`, starts MeshCentral
- Railway auto-provides `MONGO_URL` and `MONGO_DATABASE`, mapped to `MONGODB_URL` and `MONGODB_NAME` in entrypoint
- MongoDB configuration supports both Railway's environment variables and custom local values

### Directory Structure

```
trifecta/
  proxy/                         # FastAPI WebSocket-to-REST bridge service
    app.py                       # Main FastAPI application
    Dockerfile                   # Proxy service container
    railway.json                 # Proxy Railway deployment config (watchPatterns: proxy/**)
    requirements.txt             # Python dependencies (FastAPI, uvicorn, websocket-client)
  marlin/                        # Computer Use Agent deployment configs
    docker-compose-marlin.yml    # CUA VM orchestration
  meshcentral-data/              # MeshCentral runtime data
    config.json.template         # Configuration template with ${VAR} placeholders
    config.json                  # Generated config (gitignored)
  .github/
    workflows/
      security-scan.yml          # CI/CD security automation
    pre-commit-hook.sh           # Git hook for secret prevention
  check_cert.py                  # SSL certificate validation utility
  check_nginx.py                 # Nginx configuration validator
  check_redirects.py             # Redirect testing utility
  generate-config.sh             # Standalone config generation script
  docker-entrypoint.sh           # Container entrypoint (generates config + starts MeshCentral)
  docker-compose.yml             # Base orchestration (development)
  docker-compose.prod.yml        # Production overlay (restricted mounts)
  docker-compose.postgres.yml    # PostgreSQL database configuration
  index.js                       # Node.js process spawner for MeshCentral
  .env.example                   # Environment variable template
```

## Important Files

- **SECURITY.md**: Security policies, secrets management, SSL/TLS configuration, and audit checklist
- **MIGRATION.md**: Step-by-step guide for migrating from hardcoded secrets to environment-based configuration
- **.env.example**: Template for environment configuration with all available variables
- **proxy/railway.json**: Proxy service Railway config (healthcheck timeout: 100s, watchPatterns: `proxy/**`)
- **index.js**: Simple process spawner that runs `node node_modules/meshcentral` with inherited stdio

## Key Principles

1. **Security First**: Never commit secrets, certificates, or `.env` files
2. **Template-based Config**: Use `config.json.template` + environment variables for all configuration
3. **Two-tier Deployment**: Use `docker-compose.prod.yml` for production with minimal, read-only volume mounts
4. **Certificate Management**: Prefer Let's Encrypt auto-renewal; store custom certs outside repository
5. **Validation Before Deploy**: Run Python check scripts (`check_cert.py`, etc.) before deploying configuration changes

## Railway Deployment

This repository contains multiple Railway services with independent configurations:

**Proxy API Service** (`proxy/railway.json`) - Standalone Deployment:
- **Deployment**: Create separate Railway service with root directory `/proxy`
- Builder: Dockerfile (path: `Dockerfile` within proxy directory)
- Start command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
- Healthcheck: `/health` endpoint, 100s timeout
- Restart policy: ON_FAILURE with max 10 retries
- **Required env vars**:
  - `DAISYCHAIN_URL` - URL of remote MeshCentral server (e.g., `tee.up.railway.app`)
  - `DAISYCHAIN_TOKEN` - MeshCentral login token (get from MeshCentral web UI)
  - `PROXY_API_KEY` - API key for securing proxy endpoints
- **Connects remotely to MeshCentral** - No need to be co-located with MeshCentral service

**MeshCentral Service** (no railway.json in root - uses Railway dashboard config):
- Uses `docker-entrypoint.sh` to generate config and start MeshCentral
- Requires longer healthcheck timeout (MeshCentral initialization takes time)
- Required env vars: `HOSTNAME`, `LETSENCRYPT_EMAIL`, `MONGODB_URL`, `MONGODB_NAME`
- Railway auto-provides MongoDB connection via `MONGO_URL` and `MONGO_DATABASE`

**Checking Railway Logs:**
When asked to check Railway logs, wait 60 seconds, check logs with CLI, then incrementally increase wait times (90s, 120s, 150s max) until deployment succeeds, fails, or crashes. Report findings from logs.

## Integration Points

- **MeshCentral**: Core remote management platform (npm package, not custom fork)
- **Tailscale**: VPN network for team connectivity
- **Fast API**: Preferred HTTP stack for Python services
- **Ollama**: AI model endpoint at `hugo:11434`
