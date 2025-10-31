# GitHub Actions Setup Guide

This guide explains how to configure GitHub Actions workflows and secrets for the TreeTee application.

## Overview

This repository includes several GitHub Actions workflows to automate:

- **CI/CD**: Continuous integration, testing, and deployment
- **Security**: Regular security scans and secret validation
- **Docker**: Building and publishing Docker images
- **Secret Management**: Validating and rotating secrets

## Quick Start

### 1. Configure Required Secrets

Navigate to your repository on GitHub:
1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add the following required secrets:

#### Required Secrets

| Secret Name | Description | Example Value |
|------------|-------------|---------------|
| `HOSTNAME` | Your deployment domain | `treetee.yourdomain.com` |
| `LETSENCRYPT_EMAIL` | Email for Let's Encrypt SSL certificates | `admin@yourdomain.com` |

#### Optional Secrets (Deployment-Specific)

**For Railway Deployment:**

| Secret Name | Description | How to Get |
|------------|-------------|------------|
| `RAILWAY_TOKEN` | Railway API token | 1. Go to [Railway Dashboard](https://railway.app)<br>2. Account Settings → Tokens<br>3. Create new token |

**For SSH/Docker Deployment:**

| Secret Name | Description | Example Value |
|------------|-------------|---------------|
| `DEPLOY_HOST` | SSH server hostname/IP | `deploy.yourdomain.com` or `192.168.1.100` |
| `DEPLOY_USER` | SSH username | `deploy` or `ubuntu` |
| `DEPLOY_SSH_KEY` | SSH private key | Contents of your private key file |
| `DEPLOY_PATH` | Application path on server (optional) | `/opt/treetee` (default if not set) |

### 2. Generate SSH Key for Deployment (if using SSH)

If you're deploying via SSH, generate a dedicated deployment key:

```bash
# Generate SSH key pair
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/deploy_key -N ""

# Copy public key to deployment server
ssh-copy-id -i ~/.ssh/deploy_key.pub user@your-server.com

# Copy private key content to clipboard
cat ~/.ssh/deploy_key | pbcopy  # macOS
# or
cat ~/.ssh/deploy_key | xclip -selection clipboard  # Linux
# or just display it
cat ~/.ssh/deploy_key

# Add private key content as DEPLOY_SSH_KEY secret in GitHub
```

### 3. Enable GitHub Actions

1. Go to **Settings** → **Actions** → **General**
2. Under "Actions permissions", select:
   - ✅ Allow all actions and reusable workflows
3. Under "Workflow permissions", select:
   - ✅ Read and write permissions
   - ✅ Allow GitHub Actions to create and approve pull requests

### 4. Set Up Environments (Optional but Recommended)

For production deployments with additional protection:

1. Go to **Settings** → **Environments**
2. Click **New environment**
3. Name it `production`
4. Configure protection rules:
   - ✅ Required reviewers (add team members)
   - ✅ Wait timer (optional delay before deployment)
5. Add environment-specific secrets if needed

## Available Workflows

### 1. CI - Build and Test (`ci.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Manual dispatch

**What it does:**
- Installs dependencies and runs security audits
- Validates configuration scripts
- Builds Docker image for testing
- Tests configuration generation

**No secrets required** - runs on all PRs and pushes.

### 2. Security Scan (`security-scan.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Weekly schedule (Sundays at midnight)

**What it does:**
- Scans for secrets in code (TruffleHog)
- Audits npm dependencies
- Checks for committed sensitive files
- Runs CodeQL analysis

**No secrets required** - automatic security checks.

### 3. Deploy to Production (`deploy.yml`)

**Triggers:**
- Push to `main` branch (auto-deploy to Railway)
- Manual dispatch (choose environment)

**What it does:**
- Creates `.env` file from secrets
- Generates MeshCentral configuration
- Deploys to Railway or via SSH
- Runs post-deployment health checks

**Required secrets:**
- `HOSTNAME`
- `LETSENCRYPT_EMAIL`
- `RAILWAY_TOKEN` (for Railway deployment)
- OR `DEPLOY_HOST`, `DEPLOY_USER`, `DEPLOY_SSH_KEY` (for SSH deployment)

### 4. Build and Publish Docker Image (`docker-publish.yml`)

**Triggers:**
- Push to `main` or `develop`
- Tags starting with `v` (e.g., `v1.0.0`)
- Pull requests to `main`
- Manual dispatch

**What it does:**
- Builds Docker image for multiple platforms
- Publishes to GitHub Container Registry (ghcr.io)
- Tags with branch name, version, commit SHA, and `latest`

**Secrets used:**
- `GITHUB_TOKEN` (automatically provided by GitHub)

### 5. Secrets Management (`secrets-management.yml`)

**Triggers:**
- Manual dispatch (choose action)
- Monthly schedule (1st of each month)

**What it does:**
- Validates all required secrets are configured
- Generates validation reports
- Creates monthly secret rotation reminders

**No additional secrets required** - validates existing secrets.

## Testing Your Setup

### Test Secret Configuration

1. Go to **Actions** tab
2. Click **Secrets Management** workflow
3. Click **Run workflow**
4. Select `validate` action
5. Check the workflow run for validation results

### Test CI Pipeline

1. Create a new branch
2. Make a small change (e.g., update README)
3. Create a pull request
4. CI workflow should run automatically
5. Check workflow results

### Test Deployment (Staging)

1. Go to **Actions** tab
2. Click **Deploy to Production** workflow
3. Click **Run workflow**
4. Select `staging` environment
5. Confirm deployment succeeds

## Workflow Customization

### Disable Automatic Deployments

If you want to manually trigger deployments only:

Edit `.github/workflows/deploy.yml`:
```yaml
on:
  # Remove or comment out:
  # push:
  #   branches:
  #     - main
  
  # Keep only manual trigger:
  workflow_dispatch:
    # ... rest of config
```

### Change Deployment Branch

To deploy from a different branch:

Edit `.github/workflows/deploy.yml`:
```yaml
on:
  push:
    branches:
      - production  # Change from 'main' to your branch
```

### Add Deployment Notifications

You can add Slack, Discord, or email notifications to deployment workflows.

**Example: Slack notification**

Add to the end of deploy job:
```yaml
- name: Notify Slack
  if: always()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    text: 'Deployment to ${{ secrets.HOSTNAME }}'
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### Customize Secret Rotation Schedule

Edit `.github/workflows/secrets-management.yml`:
```yaml
schedule:
  # Change from monthly to weekly:
  - cron: '0 0 * * 0'  # Every Sunday
  
  # Or quarterly:
  - cron: '0 0 1 */3 *'  # Every 3 months
```

## Security Best Practices

### 1. Never Commit Secrets

❌ **Don't do this:**
```bash
# .env file in repository
HOSTNAME=mysite.com
LETSENCRYPT_EMAIL=admin@mysite.com
```

✅ **Do this instead:**
- Add secrets to GitHub Secrets Manager
- Use `.env.example` as a template
- Add `.env` to `.gitignore`

### 2. Use Environment Protection Rules

For production deployments:
- Require manual approval
- Restrict to specific branches
- Add deployment wait timers

### 3. Rotate Secrets Regularly

- Change SSH keys quarterly
- Rotate API tokens every 90 days
- Update certificates before expiration
- Use the monthly reminder workflow

### 4. Review Access Logs

Regularly check:
- GitHub Actions workflow runs
- Failed authentication attempts
- Deployment logs
- MeshCentral access logs

### 5. Limit Secret Scope

- Create deployment-specific accounts
- Use least-privilege access
- Separate staging and production secrets
- Use environment-specific secrets when possible

## Troubleshooting

### Workflow Fails: "Secret not found"

**Problem:** Required secret is not configured.

**Solution:**
```bash
# Run validation workflow
1. Go to Actions → Secrets Management
2. Run workflow with 'validate' action
3. Check which secrets are missing
4. Add missing secrets in Settings → Secrets
```

### Deployment Fails: SSH Connection

**Problem:** Cannot connect to deployment server.

**Solution:**
```bash
# Test SSH key locally
ssh -i ~/.ssh/deploy_key $DEPLOY_USER@$DEPLOY_HOST

# Verify SSH key is correct
# Check server firewall allows GitHub Actions IPs
# Ensure DEPLOY_HOST, DEPLOY_USER are correct
```

### Docker Build Fails: Out of Disk Space

**Problem:** GitHub Actions runner out of space.

**Solution:**
Add cleanup step before build:
```yaml
- name: Free disk space
  run: |
    docker system prune -af
    sudo rm -rf /usr/local/lib/android
    sudo rm -rf /usr/share/dotnet
```

### Railway Deployment Fails: Invalid Token

**Problem:** RAILWAY_TOKEN is invalid or expired.

**Solution:**
```bash
# Generate new token
1. Go to Railway Dashboard
2. Account Settings → Tokens
3. Create new token
4. Update RAILWAY_TOKEN secret in GitHub
```

### Configuration Generation Fails

**Problem:** generate-config.sh script fails.

**Solution:**
```bash
# Verify template exists
test -f meshcentral-data/config.json.template

# Ensure envsubst is available (installed in CI workflow)
# Check .env has all required variables
# Review workflow logs for specific error
```

## Migration from Manual Deployment

If you're currently deploying manually:

### 1. Back Up Current Configuration

```bash
# On your deployment server
cd /path/to/treetee
cp .env .env.backup
cp meshcentral-data/config.json meshcentral-data/config.json.backup
```

### 2. Add Secrets to GitHub

Transfer your current `.env` values to GitHub Secrets:
```bash
# For each variable in .env, create a corresponding GitHub secret
HOSTNAME=... → Create HOSTNAME secret
LETSENCRYPT_EMAIL=... → Create LETSENCRYPT_EMAIL secret
```

### 3. Test Deployment

Run the deployment workflow manually first:
```bash
# Actions → Deploy to Production → Run workflow
# Select 'staging' environment
# Verify it works before enabling auto-deploy
```

### 4. Enable Auto-Deploy

Once manual deployment succeeds:
- Push to main branch to trigger auto-deploy
- Monitor first few deployments
- Set up environment protection rules

## Getting Help

If you encounter issues:

1. **Check workflow logs**: Actions tab → Select failed workflow → View logs
2. **Validate secrets**: Run Secrets Management workflow
3. **Review documentation**:
   - [MIGRATION.md](../MIGRATION.md) - Environment setup
   - [SECURITY.md](../SECURITY.md) - Security practices
   - [README.md](../Readme.md) - General project info
4. **Open an issue**: Don't include secrets in issue reports!

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Railway Documentation](https://docs.railway.app/)
- [MeshCentral Documentation](https://meshcentral.com/docs/)
- [Docker Documentation](https://docs.docker.com/)

---

**Last Updated:** 2025-10-31

For questions or improvements to this guide, please open an issue or pull request.
