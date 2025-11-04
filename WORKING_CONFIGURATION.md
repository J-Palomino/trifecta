# Working TreeTee Configuration

**Date**: 2025-11-04
**Status**: ✅ WORKING - Agents connecting successfully

## Summary

TreeTee is successfully deployed on Railway with Linux agents connecting properly. The key to WAN mode was adding `certUrl` to the domain configuration.

## Working Configuration

### Environment Variables (.env)

```bash
# Node Environment
NODE_ENV=production

# Server Configuration
HOSTNAME=tee.up.railway.app
PORT=443
REDIRECT_PORT=80

# SSL/TLS Configuration
SSL_CERT_PATH=./certs/cert.pem
SSL_KEY_PATH=./certs/key.pem

# MeshCentral Configuration
MESHCENTRAL_CERT_NAME=tee.up.railway.app
MESHCENTRAL_PORT=443
MESHCENTRAL_REDIRECT_PORT=80

# Let's Encrypt Configuration
LETSENCRYPT_EMAIL=admin@daisy.plus
LETSENCRYPT_DOMAIN=tee.up.railway.app
LETSENCRYPT_PRODUCTION=true

# Application Settings
ALLOW_NEW_ACCOUNTS=false
ENABLE_IPKVM=false
ALLOW_LOGIN_TOKEN=true
WAN_ONLY=true

# Python Configuration
PYTHONUNBUFFERED=1
```

### MeshCentral Config Template (config.json.template)

```json
{
  "settings": {
    "cert": "${MESHCENTRAL_CERT_NAME}",
    "port": ${MESHCENTRAL_PORT},
    "redirPort": ${MESHCENTRAL_REDIRECT_PORT},
    "tlsOffload": true,
    "allowLoginToken": ${ALLOW_LOGIN_TOKEN},
    "WANonly": ${WAN_ONLY},
    "exactPort": true,
    "trustedProxy": ["0.0.0.0/0"]
  },
  "domains": {
    "": {
      "title": "TreeTee",
      "newAccounts": ${ALLOW_NEW_ACCOUNTS},
      "ipkvm": ${ENABLE_IPKVM},
      "certUrl": "https://${MESHCENTRAL_CERT_NAME}:${MESHCENTRAL_PORT}"
    }
  },
  "letsencrypt": {
    "email": "${LETSENCRYPT_EMAIL}",
    "names": "${LETSENCRYPT_DOMAIN}",
    "skipChallengeVerification": false,
    "production": ${LETSENCRYPT_PRODUCTION}
  }
}
```

### Railway Configuration (railway.json)

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "./Dockerfile"
  },
  "deploy": {
    "healthcheckTimeout": 800,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10,
    "volumeMounts": [
      {
        "mountPath": "/app/meshcentral-data",
        "volumeName": "meshcentral-data"
      },
      {
        "mountPath": "/app/meshcentral-backups",
        "volumeName": "meshcentral-backups"
      },
      {
        "mountPath": "/app/meshcentral-files",
        "volumeName": "meshcentral-files"
      }
    ]
  }
}
```

## Key Configuration Settings Explained

### 1. tlsOffload: true
**Why**: Railway handles TLS termination at the edge. MeshCentral needs to know this so it doesn't try to handle SSL itself.

### 2. certUrl in domain config
**Why**: This is the KEY to enabling WAN mode. It explicitly tells MeshCentral what URL to advertise to agents. Without this, MeshCentral defaults to LAN mode.

**Format**: `"certUrl": "https://tee.up.railway.app:443"`

### 3. WANonly: true
**Why**: Forces MeshCentral to only accept WAN connections (external agents), not LAN-only devices.

### 4. trustedProxy: ["0.0.0.0/0"]
**Why**: Railway's edge network acts as a proxy. This tells MeshCentral to trust the X-Forwarded-For headers from Railway's infrastructure.

### 5. Volume Mounts
**Why**: Data persistence across Railway deployments. Without these, user accounts and device configurations would be lost on every deployment.

## Data Storage

### Database Type
**NeDB** (file-based NoSQL database)

### Persisted Data Locations
- `/app/meshcentral-data/` - User accounts, devices, configurations, certificates
- `/app/meshcentral-backups/` - Daily automatic backups
- `/app/meshcentral-files/` - User uploaded files

### Database Files
- `meshcentral.db` - Main database (users, devices, configs)
- `meshcentral-events.db` - Event logs
- `meshcentral-power.db` - Power state tracking
- `meshcentral-stats.db` - Statistics and metrics

## Deployment URLs

- **Web UI**: https://tee.up.railway.app
- **Agent Connection**: wss://tee.up.railway.app:443
- **HTTP Redirect**: http://tee.up.railway.app (redirects to HTTPS)

## Agent Installation

### Linux/BSD
```bash
# Get install command from Web UI:
# https://tee.up.railway.app → My Account → Device Groups → Install → Linux/BSD

# Example command structure:
wget "https://tee.up.railway.app/meshagents?script=1" -O ./meshinstall.sh && chmod 755 ./meshinstall.sh && sudo -E ./meshinstall.sh https://tee.up.railway.app 'MESH_ID'
```

### Architecture Auto-Detection
The Linux install script automatically detects:
- x86_64 / amd64 → Machine ID 6 (Linux x86 64-bit)
- i686 / x86 → Machine ID 5 (Linux x86 32-bit)
- armv7l → Machine ID 25 (ARM 32-bit HardFloat)
- aarch64 → Machine ID 26 (ARM 64-bit)

## Verified Working On

- ✅ **Ubuntu/Debian** (systemd)
- ✅ **Railway Cloud Platform**
- ✅ **x86_64 Architecture**

## Common Issues and Solutions

### Issue: Agents not connecting
**Symptoms**: Agent installs successfully but doesn't appear in web UI

**Root Cause**: MeshCentral running in LAN mode instead of WAN mode

**Solution**: Ensure `certUrl` is set in domain config:
```json
"domains": {
  "": {
    "certUrl": "https://tee.up.railway.app:443"
  }
}
```

### Issue: 502 Bad Gateway
**Symptoms**: Railway returns 502 error

**Root Cause**: MeshCentral container not starting or crashing

**Solution**: Check `tlsOffload` is set to `true` for Railway deployment

### Issue: Data loss after deployment
**Symptoms**: User accounts and devices disappear after Railway redeploy

**Root Cause**: Missing volume mounts

**Solution**: Ensure `volumeMounts` are configured in `railway.json`

## Security Configuration

### Account Registration
**Status**: Disabled (`newAccounts: false`)
**Why**: Invitation-only access for security

### SSL/TLS
**Provider**: Let's Encrypt (automatic)
**Mode**: Production certificates
**Email**: admin@daisy.plus

### Pre-commit Hooks
**Location**: `.github/pre-commit-hook.sh`
**Purpose**: Prevent committing secrets (.env, .pem, .key files)

**Install**:
```bash
cp .github/pre-commit-hook.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## Deployment Process

### 1. Make Configuration Changes
```bash
# Edit .env or config.json.template
nano .env

# Regenerate config
./generate-config.sh
```

### 2. Commit Changes
```bash
git add .
git commit -m "Description of changes"
git push origin main
```

### 3. Deploy to Railway
```bash
railway up --service TreeTee --detach
```

### 4. Verify Deployment
```bash
# Check server is responding
curl -I https://tee.up.railway.app

# Check logs
railway logs --service TreeTee
```

## Performance Notes

- **Healthcheck Timeout**: 800s (MeshCentral needs time to initialize)
- **Restart Policy**: ON_FAILURE with max 10 retries
- **Auto-backup**: Daily at 23:01 UTC
- **Max Backup Size**: ~12MB (increases over time with usage)

## Next Steps for Scale

When you need to scale beyond NeDB:

1. **Add PostgreSQL**: Railway PostgreSQL addon
2. **Update config**: Add `postgres` section to config.json
3. **Migrate data**: Use MeshCentral built-in export/import commands

For now, NeDB is sufficient for small to medium deployments.

## Troubleshooting Commands

```bash
# On Linux agent machine:
sudo systemctl status meshagent
sudo journalctl -u meshagent -n 50 --no-pager
sudo netstat -tnp | grep meshagent

# On Railway:
railway logs --service TreeTee
curl -I https://tee.up.railway.app

# Local Docker test:
docker-compose up -d
docker-compose logs -f app
```

## Important Files

| File | Purpose | Git Status |
|------|---------|------------|
| `.env` | Environment variables | ❌ NEVER commit (gitignored) |
| `.env.example` | Template for .env | ✅ Committed |
| `meshcentral-data/config.json` | Generated config | ❌ NEVER commit (gitignored) |
| `meshcentral-data/config.json.template` | Config template | ✅ Committed |
| `railway.json` | Railway deployment config | ✅ Committed |
| `docker-compose.yml` | Local development | ✅ Committed |
| `docker-compose.prod.yml` | Production overlay | ✅ Committed |
| `generate-config.sh` | Config generation script | ✅ Committed |
| `docker-entrypoint.sh` | Container startup script | ✅ Committed |

## References

- **MeshCentral Docs**: https://ylianst.github.io/MeshCentral/
- **Railway Docs**: https://docs.railway.app/
- **Project Repository**: https://github.com/J-Palomino/trifecta
- **Live Deployment**: https://tee.up.railway.app

---

**This configuration is proven to work. Any changes should be tested locally first before deploying to Railway.**
