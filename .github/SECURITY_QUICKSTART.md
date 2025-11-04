# Security Quick Start Guide

**5-minute security setup for DaisyChain**

## New Developer Setup

```bash
# 1. Clone repository
git clone https://github.com/J-Palomino/trifecta.git
cd trifecta

# 2. Create environment file
cp .env.example .env

# 3. Edit .env with your values
nano .env
# Required: HOSTNAME and LETSENCRYPT_EMAIL

# 4. Generate configuration
./generate-config.sh

# 5. Install pre-commit hook (optional but recommended)
cp .github/pre-commit-hook.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# 6. Start application
docker-compose up -d
```

## Critical Rules

❌ **NEVER commit these files:**
- `.env`
- `*.pem` (certificates)
- `*.key` (private keys)
- Any file containing passwords or secrets

✅ **ALWAYS:**
- Use environment variables for secrets
- Check `git status` before committing
- Run security scans before pushing
- Review `.gitignore` includes sensitive patterns

## Quick Checks

### Before Committing
```bash
# Check for secrets
git diff --cached | grep -i "password\|secret\|key"

# Verify .env is not tracked
git status | grep .env

# Check for certificate files
git status | grep -E "\.(pem|key)$"
```

### Testing Configuration
```bash
# Verify environment loads
docker-compose config

# Check generated config
cat meshcentral-data/config.json

# Test application start
docker-compose up
```

## Common Issues

**Problem:** `config.json not found`
```bash
./generate-config.sh
```

**Problem:** Pre-commit hook rejects commit
- Review the specific error message
- Don't use `--no-verify` unless certain it's safe
- Ask for security review if unsure

**Problem:** Docker can't find environment variables
```bash
# Ensure .env exists
ls -la .env

# Reload Docker Compose
docker-compose down
docker-compose up -d
```

## Emergency: Committed a Secret

```bash
# 1. STOP - Don't push if you haven't yet
git reset HEAD~1

# 2. Remove the secret from the file
nano <file>

# 3. Add file to .gitignore if needed
echo "<filename>" >> .gitignore

# 4. Commit again
git add .
git commit -m "Fix: Remove secret"

# If already pushed - Contact team lead immediately
```

## Resources

- **Full documentation:** [SECURITY.md](../SECURITY.md)
- **Migration guide:** [MIGRATION.md](../MIGRATION.md)
- **Audit report:** [SECURITY_AUDIT_REPORT.md](../SECURITY_AUDIT_REPORT.md)
- **Environment template:** [.env.example](../.env.example)

## Questions?

1. Check the documentation above
2. Ask in team chat
3. Open an issue (don't include secrets!)

---

**Remember:** Security is everyone's responsibility! 🔒
