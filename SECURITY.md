# Security Policy

## Overview

This document outlines the security best practices and guidelines for the TreeTee platform. Following these practices will help ensure your deployment remains secure.

## Reporting Security Vulnerabilities

If you discover a security vulnerability, please report it by:
1. **DO NOT** create a public GitHub issue
2. Email the maintainers privately
3. Include detailed information about the vulnerability
4. Allow reasonable time for a fix before public disclosure

## Secrets Management

### Environment Variables

All sensitive configuration values should be stored as environment variables, never hardcoded in source files.

**Required secrets:**
- `HOSTNAME` - Your deployment domain
- `LETSENCRYPT_EMAIL` - Email for Let's Encrypt certificates
- `SSL_CERT_PATH` - Path to SSL certificate (if not using Let's Encrypt)
- `SSL_KEY_PATH` - Path to SSL private key (if not using Let's Encrypt)

### Using GitHub Secrets

For CI/CD pipelines and GitHub Actions:

1. Navigate to your repository Settings → Secrets and variables → Actions
2. Add the following secrets:
   - `HOSTNAME` - Your deployment domain
   - `LETSENCRYPT_EMAIL` - Your email address
   - `SSL_CERTIFICATE` - Base64 encoded SSL certificate (optional)
   - `SSL_PRIVATE_KEY` - Base64 encoded SSL private key (optional)
   - `RAILWAY_TOKEN` - Railway deployment token (if using Railway)

### Local Development

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Fill in your actual values in `.env`

3. **NEVER commit `.env` to version control**

4. Generate configuration files:
   ```bash
   ./generate-config.sh
   ```

## File Security

### Sensitive Files

The following files contain sensitive information and must never be committed:

- `*.pem` - SSL certificates and private keys
- `*.key` - Private keys
- `.env` - Environment variables
- `meshcentral-data/*.key` - MeshCentral private keys
- `meshcentral-data/config.json` - Contains email and domain info

### What Should Be Committed

- `.env.example` - Template with placeholder values
- `config.json.template` - Configuration template
- `*.md` - Documentation
- Source code files
- `docker-compose.yml` - With environment variable placeholders
- `.gitignore` - To exclude sensitive files

## SSL/TLS Configuration

### Option 1: Let's Encrypt (Recommended)

MeshCentral can automatically obtain and renew certificates:

1. Set `LETSENCRYPT_EMAIL` in your `.env` file
2. Set `LETSENCRYPT_DOMAIN` to your domain
3. Set `LETSENCRYPT_PRODUCTION=true` for production certificates
4. MeshCentral will handle the rest automatically

### Option 2: Custom Certificates

If you have your own certificates:

1. Store certificate files outside the repository (e.g., in `/etc/ssl/`)
2. Set `SSL_CERT_PATH` and `SSL_KEY_PATH` in `.env`
3. Ensure files have restricted permissions (600 or 400)
4. Mount certificate directory as volume in Docker

```bash
# Set restrictive permissions
chmod 600 /path/to/key.pem
chmod 644 /path/to/cert.pem
```

## Docker Security

### Best Practices

1. **Don't bind-mount the entire repository in production**
   ```yaml
   # Instead of:
   volumes:
     - .:/app
   
   # Use specific mounts:
   volumes:
     - ./meshcentral-data:/app/meshcentral-data
   ```

2. **Use secrets management for sensitive data**
   ```yaml
   secrets:
     ssl_cert:
       file: ./certs/cert.pem
     ssl_key:
       file: ./certs/key.pem
   ```

3. **Run containers as non-root user** (add to Dockerfile):
   ```dockerfile
   USER node
   ```

4. **Use Docker secrets in production:**
   ```bash
   docker secret create ssl_cert ./cert.pem
   docker secret create ssl_key ./key.pem
   ```

## Network Security

### Firewall Configuration

Ensure only necessary ports are exposed:
- Port 443 (HTTPS) - Required
- Port 80 (HTTP) - For redirect to HTTPS
- Close all other ports

### Trusted Proxies

If behind a reverse proxy, configure trusted proxy IPs in `config.json`:
```json
{
  "settings": {
    "trustedProxy": ["10.0.0.0/8"]
  }
}
```

## Access Control

### Account Security

- Set `newAccounts: false` to disable public registration
- Use strong passwords for all accounts
- Enable two-factor authentication when available
- Regularly audit user accounts and permissions

### API Security

- Use `allowLoginToken: true` only if needed for automation
- Rotate API tokens regularly
- Use short-lived tokens when possible
- Implement IP whitelisting for API access

## Deployment Security

### GitHub Actions

Example secure workflow:

```yaml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Configure environment
        run: |
          echo "HOSTNAME=${{ secrets.HOSTNAME }}" >> .env
          echo "LETSENCRYPT_EMAIL=${{ secrets.LETSENCRYPT_EMAIL }}" >> .env
          ./generate-config.sh
      
      - name: Deploy to Railway
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
        run: |
          railway up
```

### Railway Deployment

Store secrets in Railway environment variables:
1. Navigate to your Railway project
2. Go to Variables tab
3. Add all required environment variables
4. Railway will automatically use them during deployment

## Audit Checklist

Regular security audits should verify:

- [ ] No hardcoded secrets in source code
- [ ] `.env` file is not committed to git
- [ ] All `.pem` and `.key` files are gitignored
- [ ] SSL certificates are valid and not expired
- [ ] Only necessary ports are exposed
- [ ] Strong passwords are enforced
- [ ] Access logs are monitored
- [ ] Dependencies are up to date
- [ ] Docker images are from trusted sources
- [ ] Backup files are encrypted

## Cleaning Git History

If secrets were accidentally committed, clean them from history:

```bash
# Install BFG Repo-Cleaner
# https://rtyley.github.io/bfg-repo-cleaner/

# Remove specific files from history
bfg --delete-files "*.pem"
bfg --delete-files "*.key"

# Or use git-filter-repo (recommended)
git filter-repo --path cert.pem --invert-paths
git filter-repo --path key.pem --invert-paths

# Force push changes (coordinate with team first!)
git push --force --all
git push --force --tags
```

⚠️ **Warning:** Rewriting git history affects all repository users. Coordinate with your team before force-pushing.

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Docker Security Best Practices](https://docs.docker.com/develop/security-best-practices/)
- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [MeshCentral Security Guide](https://meshcentral.com/docs/MeshCentral2SecurityFeatures.pdf)

## Contact

For security concerns, please contact the repository maintainers:
- Open a security advisory on GitHub (preferred for vulnerabilities)
- Email: [Repository owner's email - to be configured]

---

Last updated: 2024-10-30
