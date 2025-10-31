# Security Migration Guide

This guide helps you migrate from hardcoded secrets to environment-based configuration.

## Overview

This repository has been updated to use environment variables and GitHub secrets instead of hardcoded values. This improves security by:
- Keeping secrets out of version control
- Allowing different configurations per environment
- Enabling secure CI/CD pipelines
- Following security best practices

## Migration Steps

### Step 1: Backup Current Configuration

```bash
# Backup your current config
cp meshcentral-data/config.json meshcentral-data/config.json.backup

# Backup any certificate files
mkdir -p ~/trifecta-certs-backup
cp *.pem ~/trifecta-certs-backup/ 2>/dev/null || true
```

### Step 2: Create Environment File

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your actual values
nano .env  # or use your preferred editor
```

Fill in these required values:
```bash
HOSTNAME=your-domain.com
LETSENCRYPT_EMAIL=your-email@example.com
```

### Step 3: Move Certificates (Optional)

If you have existing certificates:

```bash
# Create a certs directory outside the repository
mkdir -p ~/trifecta-certs
mv cert.pem ~/trifecta-certs/
mv key.pem ~/trifecta-certs/

# Update .env to point to new location
echo "SSL_CERT_PATH=$HOME/trifecta-certs/cert.pem" >> .env
echo "SSL_KEY_PATH=$HOME/trifecta-certs/key.pem" >> .env
```

### Step 4: Generate New Configuration

```bash
# Generate config.json from template
./generate-config.sh
```

This will create `meshcentral-data/config.json` from the template using your environment variables.

### Step 5: Update Docker Configuration

The `docker-compose.yml` file now uses environment variables. Update any custom configurations:

```bash
# Test the configuration
docker-compose config

# Start the application
docker-compose up -d
```

### Step 6: Verify Everything Works

```bash
# Check that the application started
docker-compose ps

# Check logs for errors
docker-compose logs -f

# Test HTTPS access
curl -k https://localhost
```

### Step 7: Clean Committed Secrets (Important!)

**WARNING:** This rewrites git history. Coordinate with your team first!

If secrets were committed to git, remove them:

```bash
# Option 1: Using git-filter-repo (recommended)
# Install: pip install git-filter-repo

git filter-repo --path cert.pem --invert-paths
git filter-repo --path key.pem --invert-paths
git filter-repo --path 'meshcentral-data/*.key' --invert-paths

# Option 2: Using BFG Repo-Cleaner
# Download from: https://rtyley.github.io/bfg-repo-cleaner/

bfg --delete-files cert.pem
bfg --delete-files key.pem
bfg --delete-files '*.key'

# After using either tool, clean up
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push (WARNING: affects all users)
git push origin --force --all
git push origin --force --tags
```

### Step 8: Rotate Secrets

Since secrets were in version control, you should rotate them:

1. **Generate new SSL certificates:**
   ```bash
   # Let MeshCentral generate new Let's Encrypt certs
   # Or generate new self-signed certs:
   openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
   ```

2. **Update MeshCentral admin password:**
   - Log into MeshCentral
   - Go to My Account → Change Password
   - Use a strong, unique password

3. **Regenerate any API tokens or access keys**

### Step 9: Setup GitHub Secrets

For CI/CD and GitHub Actions:

1. Go to your repository on GitHub
2. Navigate to: Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Add these secrets:

#### Required Secrets

| Secret Name | Description | Example Value |
|------------|-------------|---------------|
| `HOSTNAME` | Your deployment domain | `tee.yourdomain.com` |
| `LETSENCRYPT_EMAIL` | Your email for Let's Encrypt | `admin@yourdomain.com` |

#### Optional Secrets (Deployment-Specific)

| Secret Name | Description | When Needed |
|------------|-------------|-------------|
| `RAILWAY_TOKEN` | Railway deployment token | For Railway deployment |
| `DEPLOY_HOST` | SSH server hostname | For SSH/Docker deployment |
| `DEPLOY_USER` | SSH username | For SSH/Docker deployment |
| `DEPLOY_SSH_KEY` | SSH private key | For SSH/Docker deployment |
| `DEPLOY_PATH` | Application path on server | For SSH deployment (optional, default: /opt/treetee) |

**📚 For detailed GitHub Actions setup instructions, see [.github/ACTIONS_SETUP.md](.github/ACTIONS_SETUP.md)**

### Step 10: Update Documentation

Update any internal documentation or deployment guides to reference:
- The new `.env` file approach
- Location of certificates
- GitHub secrets configuration
- The `generate-config.sh` script

## For New Deployments

If you're setting up a fresh deployment:

1. Clone the repository
2. Copy `.env.example` to `.env`
3. Fill in your configuration values
4. Run `./generate-config.sh`
5. Start with `docker-compose up -d`

## For Railway Deployments

1. In Railway dashboard, go to your project
2. Click on Variables
3. Add all environment variables from `.env.example`
4. Railway will automatically redeploy

## Troubleshooting

### Problem: "config.json not found"

**Solution:**
```bash
./generate-config.sh
```

### Problem: "SSL certificate errors"

**Solution:**
```bash
# Check certificate paths in .env
cat .env | grep SSL

# Verify files exist
ls -l $(grep SSL_CERT_PATH .env | cut -d= -f2)
ls -l $(grep SSL_KEY_PATH .env | cut -d= -f2)

# Or let MeshCentral use Let's Encrypt
# Remove SSL_CERT_PATH and SSL_KEY_PATH from .env
```

### Problem: "Environment variables not loaded"

**Solution:**
```bash
# Verify .env file exists
ls -la .env

# Check Docker loads the env file
docker-compose config

# Restart containers
docker-compose down
docker-compose up -d
```

### Problem: "Permission denied on generate-config.sh"

**Solution:**
```bash
chmod +x generate-config.sh
```

## Rolling Back

If you need to roll back to the previous configuration:

```bash
# Restore backup config
cp meshcentral-data/config.json.backup meshcentral-data/config.json

# Restart
docker-compose restart
```

## Additional Security Steps

After migration, consider:

1. **Enable 2FA** for all admin accounts
2. **Review access logs** regularly
3. **Setup monitoring** and alerts
4. **Regular backups** of configuration and data
5. **Keep dependencies updated** with `npm audit fix`
6. **Review firewall rules** to only expose necessary ports

## Getting Help

If you encounter issues:
1. Check the logs: `docker-compose logs -f`
2. Review `SECURITY.md` for best practices
3. Open an issue on GitHub (don't include secrets!)
4. Contact the maintainers

## Verification Checklist

After migration, verify:

- [ ] `.env` file created with correct values
- [ ] `.env` is gitignored (not tracked by git)
- [ ] `config.json` generated successfully
- [ ] Application starts without errors
- [ ] HTTPS is working correctly
- [ ] No secrets in git history (or cleaned if found)
- [ ] GitHub secrets configured (if using CI/CD)
- [ ] Certificates secured with proper permissions
- [ ] Old certificates rotated (if they were committed)
- [ ] Team members notified of changes
- [ ] Documentation updated

---

**Security Note:** This migration significantly improves your security posture, but remember to follow all steps, especially rotating any secrets that were previously committed to version control.
