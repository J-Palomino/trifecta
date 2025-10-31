# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TreeTee is an AI agent monitoring and control platform that bridges AI agents, virtual machines, and human control. It enables AI agents to control computers via VNC/RDP while providing secure monitoring in Trusted Execution Environments (TEEs).

**Core Components:**
- MeshCentral-based remote device management server
- Node.js proxy layer for handling connections
- Python utilities for certificate and connection validation
- Docker containerized deployment

## Development Commands

### Build and Run

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
```

### Configuration

```bash
# Generate config from environment variables
./generate-config.sh

# Verify Docker compose configuration
docker-compose config
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

### Pre-commit Hook

Install the security pre-commit hook to prevent committing secrets:
```bash
cp .github/pre-commit-hook.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## Architecture

### Deployment Stack

1. **Dockerfile**: Node 18 base with Python 3 for utilities
2. **docker-compose.yml**: Base configuration with environment variables
3. **docker-compose.prod.yml**: Production overlay with restricted volume mounts and logging
4. **index.js**: Simple Node.js process spawner that launches MeshCentral

### Configuration Management

- **Environment Variables**: All secrets and configuration values in `.env` (never committed)
- **Template System**: `meshcentral-data/config.json.template` + `generate-config.sh` generates `config.json`
- **Dynamic Configuration**: Config generated from environment variables at deployment time

Key environment variables:
- `HOSTNAME`: Deployment domain
- `LETSENCRYPT_EMAIL`: Email for SSL certificate registration
- `NODE_ENV`: Environment mode (production/development)
- `MESHCENTRAL_PORT`: HTTPS port (default: 443)
- `ALLOW_NEW_ACCOUNTS`: Enable/disable user registration

### Security Model

This repository follows strict security practices:

1. **No Hardcoded Secrets**: All sensitive data via environment variables
2. **Certificate Management**: SSL/TLS certs never committed; use Let's Encrypt or external paths
3. **Pre-commit Hooks**: Automated scanning for secrets in staged changes
4. **CI/CD Security Scans**:
   - TruffleHog for secret detection
   - npm audit for dependency vulnerabilities
   - CodeQL for code analysis
   - File scanning for sensitive patterns

### Directory Structure

```
trifecta/
  meshcentral-data/         # MeshCentral runtime data (certs, DB, agents)
    config.json.template    # Configuration template
    config.json            # Generated config (never committed)
  .github/
    workflows/             # CI/CD automation
    pre-commit-hook.sh     # Git hook for secret prevention
  check_*.py              # Python validation utilities
  generate-config.sh      # Configuration generation script
  Dockerfile             # Container definition
  docker-compose.yml     # Base orchestration
  docker-compose.prod.yml # Production overlay
  index.js               # MeshCentral launcher
```

## Important Files

- **SECURITY.md**: Security policies, best practices, and secrets management guidelines
- **MIGRATION.md**: Guide for migrating from hardcoded secrets to environment-based configuration
- **.env.example**: Template for environment configuration
- **railway.json**: Railway deployment configuration

## Key Principles

1. **Security First**: Never commit secrets, certificates, or `.env` files
2. **Environment-Based Config**: Use templates + environment variables for all configuration
3. **Production Security**: Use `docker-compose.prod.yml` for production with minimal volume mounts
4. **Certificate Management**: Prefer Let's Encrypt auto-renewal; store custom certs outside repository
5. **Validation**: Run Python check scripts before deploying configuration changes

## Railway Deployment

This project is configured for Railway deployment:
- Set environment variables in Railway dashboard
- Railway automatically builds using Dockerfile
- Healthcheck timeout: 800s
- Restart policy: ON_FAILURE with 10 max retries

## Integration Points

- **MeshCentral**: Core remote management platform (npm package)
- **Tailscale**: VPN network for team connectivity
- **Fast API**: Preferred HTTP stack for Python services
- **Ollama**: AI model endpoint at `hugo:11434`
