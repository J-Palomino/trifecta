# GitHub Actions Workflows Summary

This document provides a quick overview of all GitHub Actions workflows implemented in this repository.

## Quick Reference

| Workflow | File | Trigger | Purpose |
|----------|------|---------|---------|
| CI - Build and Test | `ci.yml` | Push/PR to main/develop | Automated testing and validation |
| Deploy to Production | `deploy.yml` | Push to main, Manual | Deploy to Railway or SSH |
| Docker Image Build | `docker-publish.yml` | Push/Tags/Manual | Build and publish Docker images |
| Secrets Management | `secrets-management.yml` | Manual, Monthly | Validate and manage secrets |
| Security Scan | `security-scan.yml` | Push/PR/Weekly | Security scanning and audits |

## Workflow Details

### 1. CI - Build and Test (`ci.yml`)

**Purpose**: Continuous integration testing and validation

**Triggers**:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Manual dispatch

**Jobs**:
- `test`: Install dependencies, run security audits, verify scripts
- `build-docker`: Build Docker image for testing
- `validate-config`: Test configuration generation

**Required Secrets**: None (runs on all PRs)

**What it validates**:
- ✅ npm dependencies install correctly
- ✅ No critical security vulnerabilities
- ✅ Docker image builds successfully
- ✅ Configuration scripts work
- ✅ docker-compose configuration is valid

---

### 2. Deploy to Production (`deploy.yml`)

**Purpose**: Automated deployment to production or staging environments

**Triggers**:
- Automatic: Push to `main` branch (deploys to Railway)
- Manual: Workflow dispatch with environment selection

**Jobs**:
- `deploy-railway`: Deploy to Railway platform
- `deploy-docker`: Deploy via SSH to Docker host
- `post-deploy-checks`: Health checks after deployment

**Required Secrets**:
- `HOSTNAME` - Deployment domain
- `LETSENCRYPT_EMAIL` - SSL certificate email

**Optional Secrets** (deployment method specific):
- `RAILWAY_TOKEN` - For Railway deployment
- `DEPLOY_HOST` - SSH server hostname
- `DEPLOY_USER` - SSH username
- `DEPLOY_SSH_KEY` - SSH private key
- `DEPLOY_PATH` - Application path (default: /opt/treetee)

**What it does**:
1. Creates `.env` file from secrets
2. Generates MeshCentral configuration
3. Deploys to selected platform
4. Runs health checks
5. Reports deployment status

---

### 3. Build and Publish Docker Image (`docker-publish.yml`)

**Purpose**: Build multi-platform Docker images and publish to GitHub Container Registry

**Triggers**:
- Push to `main` or `develop` branches
- Tags starting with `v` (e.g., `v1.0.0`)
- Pull requests to `main` (build only, no push)
- Manual dispatch

**Jobs**:
- `build-and-push`: Build Docker image for multiple platforms

**Required Secrets**:
- `GITHUB_TOKEN` (automatically provided)

**Features**:
- Multi-platform builds (linux/amd64, linux/arm64)
- Automatic tagging:
  - Branch name (e.g., `main`, `develop`)
  - Semantic version from tags (e.g., `v1.0.0` → `1.0.0`, `1.0`, `1`)
  - Commit SHA with branch prefix (e.g., `main-abc1234`)
  - `latest` tag for default branch
- Build caching for faster builds
- Publishes to `ghcr.io/<owner>/<repo>`

**Image Access**:
```bash
# Pull the latest image
docker pull ghcr.io/j-palomino/trifecta:latest

# Pull a specific version
docker pull ghcr.io/j-palomino/trifecta:v1.0.0

# Pull a branch version
docker pull ghcr.io/j-palomino/trifecta:develop
```

---

### 4. Secrets Management (`secrets-management.yml`)

**Purpose**: Validate secrets configuration and provide rotation reminders

**Triggers**:
- Manual dispatch with action selection
- Monthly schedule (1st of each month at midnight)

**Jobs**:
- `validate-secrets`: Check that required secrets are configured
- `rotation-reminder`: Generate monthly secret rotation reminders

**Required Secrets**: 
- None (validates existing secrets)

**What it validates**:
- ✅ `HOSTNAME` is configured
- ✅ `LETSENCRYPT_EMAIL` is configured
- ⚠️ Optional secrets status (RAILWAY_TOKEN, SSH deployment secrets)

**Validation Actions**:
```bash
# To manually validate secrets:
# 1. Go to Actions tab
# 2. Select "Secrets Management" workflow
# 3. Click "Run workflow"
# 4. Choose "validate" action
# 5. View validation report in workflow summary
```

**Rotation Reminder**:
- Runs automatically on the 1st of each month
- Provides checklist of secrets to rotate
- Links to security documentation
- Can be run manually anytime

---

### 5. Security Scan (`security-scan.yml`)

**Purpose**: Comprehensive security scanning and vulnerability detection

**Triggers**:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Weekly schedule (Sundays at midnight)

**Jobs**:
- `secret-scan`: Scan for committed secrets using TruffleHog
- `dependency-audit`: Audit npm dependencies for vulnerabilities
- `file-scan`: Check for sensitive files in version control
- `code-scan`: CodeQL static analysis for JavaScript and Python

**Required Secrets**: None

**What it checks**:
- 🔍 Secrets or credentials in code (TruffleHog)
- 🔍 npm package vulnerabilities (npm audit)
- 🔍 Committed `.env`, certificates, or key files
- 🔍 Code vulnerabilities (CodeQL)

**Security Levels**:
- Critical vulnerabilities fail the build
- High vulnerabilities reported but allow continuation
- Moderate/low vulnerabilities logged

---

## Setting Up Workflows

### Step 1: Configure Required Secrets

Go to **Settings** → **Secrets and variables** → **Actions** and add:

**Required (Minimum)**:
```
HOSTNAME = your-domain.com
LETSENCRYPT_EMAIL = admin@your-domain.com
```

### Step 2: Choose Deployment Method

**Option A: Railway Deployment**
```
RAILWAY_TOKEN = your_railway_token
```

**Option B: SSH/Docker Deployment**
```
DEPLOY_HOST = your-server.com
DEPLOY_USER = deploy
DEPLOY_SSH_KEY = <your SSH private key>
DEPLOY_PATH = /opt/treetee  # Optional, defaults to /opt/treetee
```

### Step 3: Enable Workflows

1. Go to **Settings** → **Actions** → **General**
2. Select "Allow all actions and reusable workflows"
3. Enable "Read and write permissions"
4. Enable "Allow GitHub Actions to create and approve pull requests"

### Step 4: Test Workflows

1. **Test CI**: Create a PR and verify CI workflow runs
2. **Test Secret Validation**: Run Secrets Management workflow with "validate" action
3. **Test Deployment**: Run Deploy workflow manually to staging first

---

## Workflow Status Badges

Add these badges to your README.md:

```markdown
![CI](https://github.com/J-Palomino/trifecta/workflows/CI%20-%20Build%20and%20Test/badge.svg)
![Security](https://github.com/J-Palomino/trifecta/workflows/Security%20Scan/badge.svg)
![Deploy](https://github.com/J-Palomino/trifecta/workflows/Deploy%20to%20Production/badge.svg)
```

---

## Common Workflows Usage

### Deploying to Production

**Automatic** (on push to main):
```bash
git push origin main
# Deployment workflow triggers automatically
```

**Manual**:
1. Go to **Actions** → **Deploy to Production**
2. Click **Run workflow**
3. Select `production` environment
4. Click **Run workflow**

### Building Docker Images

**Automatic** (on push):
```bash
git push origin main
# Docker image build triggers automatically
```

**For a release**:
```bash
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
# Builds and tags as 1.0.0, 1.0, 1, and latest
```

### Validating Secrets

1. Go to **Actions** → **Secrets Management**
2. Click **Run workflow**
3. Select `validate` action
4. View results in workflow summary

### Running Security Scans

**Automatic**:
- Runs on every push/PR
- Weekly scan on Sundays

**Manual**:
1. Go to **Actions** → **Security Scan**
2. Click **Run workflow**

---

## Troubleshooting

### Workflow Failed: Missing Secrets

**Solution**: Run secrets validation workflow to identify missing secrets.

### Deployment Failed: SSH Connection

**Solution**:
1. Verify `DEPLOY_HOST`, `DEPLOY_USER`, and `DEPLOY_SSH_KEY` are correct
2. Test SSH connection manually: `ssh user@host`
3. Check server firewall allows GitHub Actions IPs

### Docker Build Failed

**Solution**:
1. Check Dockerfile syntax
2. Verify base image is accessible
3. Review workflow logs for specific error

### Security Scan Failed

**Solution**:
1. Review CodeQL or TruffleHog findings
2. Fix reported vulnerabilities
3. Re-run workflow

---

## Best Practices

1. **Always test in staging first** - Use manual deployment to staging before production
2. **Monitor workflow runs** - Check Actions tab regularly for failures
3. **Rotate secrets regularly** - Use monthly reminder workflow
4. **Review security scans** - Address findings promptly
5. **Use environment protection** - Set up required reviewers for production
6. **Keep workflows updated** - Update action versions periodically

---

## Additional Resources

- **[ACTIONS_SETUP.md](ACTIONS_SETUP.md)** - Detailed setup guide
- **[MIGRATION.md](../MIGRATION.md)** - Environment setup and migration
- **[SECURITY.md](../SECURITY.md)** - Security best practices
- **[Readme.md](../Readme.md)** - Project overview

---

**Last Updated**: 2025-10-31

For questions or improvements, please open an issue or pull request.
