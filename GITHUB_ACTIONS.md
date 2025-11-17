# GitHub Actions - Container Image Building

This repository uses GitHub Actions to automatically build and publish Docker images to GitHub Container Registry (ghcr.io) whenever code is pushed.

## Workflows

### 1. Build MeshCentral Image
**File:** `.github/workflows/build-meshcentral.yml`

**Triggers:**
- Push to `main` or `dev` branches when these files change:
  - `Dockerfile`
  - `docker-entrypoint.sh`
  - `package*.json`
  - `index.js`
  - `meshcentral-data/config.json.template`
- Pull requests to `main` branch
- Manual trigger via workflow_dispatch

**Output Image:**
```
ghcr.io/j-palomino/trifecta/meshcentral:latest
ghcr.io/j-palomino/trifecta/meshcentral:main
ghcr.io/j-palomino/trifecta/meshcentral:dev
ghcr.io/j-palomino/trifecta/meshcentral:main-<commit-sha>
```

### 2. Build Proxy API Image
**File:** `.github/workflows/build-proxy.yml`

**Triggers:**
- Push to `main` or `dev` branches when files in `proxy/` change
- Pull requests to `main` branch
- Manual trigger via workflow_dispatch

**Output Image:**
```
ghcr.io/j-palomino/trifecta/proxy:latest
ghcr.io/j-palomino/trifecta/proxy:main
ghcr.io/j-palomino/trifecta/proxy:dev
ghcr.io/j-palomino/trifecta/proxy:main-<commit-sha>
```

### 3. Security Scan
**File:** `.github/workflows/security-scan.yml`

**Triggers:**
- Push to `main` or `dev` branches
- Pull requests
- Weekly schedule (Sundays at midnight)

**Checks:**
- Secret scanning with TruffleHog
- npm dependency audit
- Sensitive file detection (.env, .pem, .key files)
- CodeQL static code analysis

## How It Works

### Automatic Image Building

1. **Developer pushes code to GitHub:**
   ```bash
   git add .
   git commit -m "Update proxy API"
   git push origin main
   ```

2. **GitHub Actions automatically:**
   - Detects which files changed
   - Triggers relevant workflow (MeshCentral or Proxy)
   - Builds Docker image with Buildx
   - Pushes to GitHub Container Registry
   - Tags image with branch name and commit SHA
   - Creates multi-platform images (amd64, arm64)

3. **Images are available at:**
   - https://github.com/J-Palomino/trifecta/pkgs/container/trifecta%2Fmeshcentral
   - https://github.com/J-Palomino/trifecta/pkgs/container/trifecta%2Fproxy

## Using the Images

### Pull from GitHub Container Registry

```bash
# Pull MeshCentral image
docker pull ghcr.io/j-palomino/trifecta/meshcentral:latest

# Pull Proxy API image
docker pull ghcr.io/j-palomino/trifecta/proxy:latest

# Pull specific version
docker pull ghcr.io/j-palomino/trifecta/proxy:main-abc1234
```

### Run Locally

**MeshCentral:**
```bash
docker run -d \
  -p 443:443 -p 80:80 \
  -e HOSTNAME=localhost \
  -e LETSENCRYPT_EMAIL=admin@example.com \
  -e MONGODB_URL=mongodb://localhost:27017/meshcentral \
  -v ./meshcentral-data:/app/meshcentral-data \
  ghcr.io/j-palomino/trifecta/meshcentral:latest
```

**Proxy API:**
```bash
docker run -d \
  -p 8000:8000 \
  -e DAISYCHAIN_URL=tee.up.railway.app \
  -e DAISYCHAIN_TOKEN=your-token \
  -e PROXY_API_KEY=your-api-key \
  ghcr.io/j-palomino/trifecta/proxy:latest
```

### Deploy to Railway Using Images

#### Option 1: Railway Dashboard

1. **Create New Service**
2. **Select "Deploy from Image"**
3. **Image URL:**
   ```
   ghcr.io/j-palomino/trifecta/proxy:latest
   ```
4. **Set Environment Variables** (as documented)
5. **Deploy**

#### Option 2: Railway CLI

```bash
# Link to your project
railway link

# Deploy using Docker image
railway up --image ghcr.io/j-palomino/trifecta/proxy:latest

# Set environment variables
railway variables set DAISYCHAIN_URL=tee.up.railway.app
railway variables set DAISYCHAIN_TOKEN=your-token
railway variables set PROXY_API_KEY=your-key
```

#### Option 3: Update railway.json to Use Pre-built Images

**For Proxy (`proxy/railway.json`):**
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "image": "ghcr.io/j-palomino/trifecta/proxy:latest",
    "startCommand": "uvicorn app:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

**For MeshCentral (`railway.json`):**
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "image": "ghcr.io/j-palomino/trifecta/meshcentral:latest",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

## Image Features

### Multi-Platform Support
Both images support:
- `linux/amd64` (x86_64)
- `linux/arm64` (ARM64/Apple Silicon)

Docker automatically pulls the correct architecture for your system.

### Build Caching
GitHub Actions uses layer caching to speed up builds:
- First build: ~5-10 minutes
- Subsequent builds: ~1-3 minutes (if dependencies unchanged)

### Image Optimization
- Production-ready base images (Node 18-slim, Python 3.11-slim)
- Multi-stage builds where applicable
- Minimal attack surface
- Non-root user for proxy service
- Health checks built-in

## Permissions

### GitHub Actions Permissions
The workflows require these permissions (automatically granted):
- `contents: read` - To checkout code
- `packages: write` - To push to GitHub Container Registry

### Container Registry Access

**Public Images (Default):**
Anyone can pull images without authentication:
```bash
docker pull ghcr.io/j-palomino/trifecta/proxy:latest
```

**Private Images (If Changed to Private):**
Requires GitHub Personal Access Token:
```bash
# Login to ghcr.io
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Pull image
docker pull ghcr.io/j-palomino/trifecta/proxy:latest
```

## Making Images Public

By default, new images are private. To make them public:

1. Go to https://github.com/J-Palomino/trifecta/pkgs/container/trifecta%2Fproxy
2. Click "Package settings"
3. Scroll to "Danger Zone"
4. Click "Change visibility" → "Public"
5. Repeat for MeshCentral image

## Versioning Strategy

### Tag Format

| Tag | Description | Example |
|-----|-------------|---------|
| `latest` | Latest build from default branch (main) | `proxy:latest` |
| `main` | Latest build from main branch | `proxy:main` |
| `dev` | Latest build from dev branch | `proxy:dev` |
| `main-<sha>` | Specific commit from main | `proxy:main-abc1234` |
| `dev-<sha>` | Specific commit from dev | `proxy:dev-abc1234` |

### Recommended Usage

**Production:** Use specific commit SHAs for reproducibility
```bash
docker pull ghcr.io/j-palomino/trifecta/proxy:main-abc1234
```

**Development/Testing:** Use branch tags for latest updates
```bash
docker pull ghcr.io/j-palomino/trifecta/proxy:dev
```

**Railway Auto-deploy:** Use `latest` tag
```json
"image": "ghcr.io/j-palomino/trifecta/proxy:latest"
```

## Manual Workflow Trigger

You can manually trigger image builds without pushing code:

1. Go to GitHub → Actions tab
2. Select workflow (Build MeshCentral Image or Build Proxy API Image)
3. Click "Run workflow"
4. Select branch
5. Click "Run workflow" button

This is useful for:
- Rebuilding images with base image updates
- Testing workflow changes
- Creating images from specific branches

## Monitoring Builds

### GitHub Actions UI

1. Go to repository → Actions tab
2. View running/completed workflows
3. Click on workflow run to see details
4. View build logs, timings, and artifacts

### Build Summary

Each successful build generates a summary with:
- Image name and registry
- All generated tags
- Pull command
- Railway deployment instructions

### Notifications

Configure GitHub notifications:
1. Repository → Settings → Notifications
2. Enable "Actions" notifications
3. Choose email or web notifications

## Troubleshooting

### Build Fails with "permission denied"

**Solution:** Ensure `GITHUB_TOKEN` has package write permissions
- This is automatically provided by GitHub Actions
- Check workflow permissions in workflow file

### Image Not Found After Push

**Solutions:**
1. Check if workflow completed successfully (Actions tab)
2. Verify image visibility (should be public)
3. Check image name matches repository name

### Railway Can't Pull Image

**Solutions:**
1. Make image public in GitHub Container Registry
2. Or add GitHub PAT to Railway secrets:
   ```bash
   railway variables set GHCR_TOKEN=<your-github-pat>
   ```

### Build Takes Too Long

**Solutions:**
1. Check if base images need updating (forces rebuild)
2. Verify cache is working (check "cache hit" in logs)
3. Consider reducing image size (remove unused dependencies)

## Cost Considerations

### GitHub Actions Minutes
- **Free tier:** 2,000 minutes/month for public repositories
- **Typical build time:** 3-5 minutes per image
- **Estimated builds:** ~400 builds/month on free tier

### GitHub Container Registry Storage
- **Free tier:** Unlimited public storage
- **Private storage:** 500 MB free, then $0.25/GB/month

## Security Best Practices

### 1. Don't Commit Secrets
Never add secrets to Dockerfiles or source code:
```dockerfile
# BAD - Never do this
ENV API_KEY=secret123

# GOOD - Use build args or runtime env vars
ARG API_KEY
ENV API_KEY=${API_KEY}
```

### 2. Scan Images for Vulnerabilities
Enable Dependabot:
```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "weekly"
```

### 3. Use Specific Base Image Versions
```dockerfile
# Instead of
FROM python:3.11

# Use specific digest
FROM python:3.11@sha256:abc123...
```

### 4. Sign Images (Advanced)
Use Docker Content Trust:
```bash
export DOCKER_CONTENT_TRUST=1
docker push ghcr.io/j-palomino/trifecta/proxy:latest
```

## Next Steps

1. **Push code to GitHub** - Images will build automatically
2. **Check Actions tab** - Monitor build progress
3. **Make images public** - Allow Railway to pull without authentication
4. **Update Railway** - Switch to using pre-built images
5. **Set up auto-deploy** - Railway can auto-deploy when new images are pushed

## Additional Resources

- [GitHub Container Registry Documentation](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [Railway Docker Deployment](https://docs.railway.app/deploy/deployments#docker-builds)
