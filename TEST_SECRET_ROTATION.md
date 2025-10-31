# Secret Rotation Testing Guide

This guide helps you verify that all secrets have been successfully rotated from your repository.

## Quick Test (Automated)

Run the automated test script:

```bash
# Make the script executable
chmod +x test-secret-rotation.sh

# Run the tests
./test-secret-rotation.sh
```

This script will check:
- No secret files committed
- No secrets in git history
- .gitignore is properly configured
- Pre-commit hooks are set up
- Configuration templates are used
- Fresh deployment works
- Docker configuration is valid

## Manual Testing Steps

### 1. Scan Repository for Secrets

```bash
# Check for .env files
git ls-files | grep -E '\.env$'
# Should return nothing

# Check for certificates and keys
git ls-files | grep -E '\.(pem|key|crt|p12|pfx)$'
# Should return nothing

# Check for MeshCentral private keys
git ls-files meshcentral-data/ | grep -E 'private\.key'
# Should return nothing
```

### 2. Scan Git History

```bash
# Install TruffleHog (if not already installed)
pip install trufflehog

# Scan entire git history for secrets
trufflehog git file://. --json --no-update

# Alternative: Manual history search for private keys
git log -p --all | grep -E "BEGIN.*PRIVATE KEY"
# Should return nothing

# Search for potential email addresses (excluding examples)
git log -p --all | grep -oE "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}" | grep -v "example.com" | sort -u
# Review output - should only show placeholder emails
```

### 3. Test Pre-commit Hook

```bash
# Install the hook
cp .github/pre-commit-hook.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# Test the hook by attempting to commit a secret
echo "SECRET_KEY=mysecretkey123" > test-secret.env
git add test-secret.env
git commit -m "test commit"
# Should FAIL with error message

# Clean up test
git reset HEAD test-secret.env
rm test-secret.env
```

### 4. Test Fresh Deployment

This simulates deploying to a new environment without any old secrets:

```bash
# Create a fresh test directory
mkdir -p ~/test-trifecta-rotation
cd ~/test-trifecta-rotation

# Clone the repository
git clone <your-repo-url> .

# Verify no secrets are present
ls -la *.pem *.key 2>/dev/null
# Should return "No such file or directory"

cat .env 2>/dev/null
# Should return "No such file or directory"

# Create new environment configuration
cp .env.example .env

# Edit with NEW values (simulate rotation)
nano .env
# Set:
# - HOSTNAME=test-localhost.com
# - LETSENCRYPT_EMAIL=test@example.com
# - Use NEW certificate paths or Let's Encrypt

# Generate configuration
./generate-config.sh

# Verify config was generated without errors
cat meshcentral-data/config.json
# Should show your test values from .env

# Test Docker deployment
docker-compose config
# Should complete without errors

docker-compose up -d
# Should start successfully

# Check logs for any certificate or secret errors
docker-compose logs | grep -i "error\|fail\|certificate"

# Clean up
docker-compose down
cd ~
rm -rf ~/test-trifecta-rotation
```

### 5. Verify Environment Variable Usage

```bash
# Check that all configs use environment variables
grep -r "HOSTNAME" docker-compose.yml docker-compose.prod.yml
# Should show: ${HOSTNAME}

# Check template uses env vars
grep -E "\\\${[A-Z_]+}" meshcentral-data/config.json.template
# Should show all environment variable placeholders

# Verify generated config doesn't have placeholders
if [ -f meshcentral-data/config.json ]; then
    grep -E "\\\${[A-Z_]+}" meshcentral-data/config.json
    # Should return nothing (all vars should be substituted)
fi
```

### 6. Test with New Certificates

Generate new test certificates to verify old ones aren't being used:

```bash
# Generate new self-signed certificates
openssl req -x509 -newkey rsa:4096 -keyout test-key.pem -out test-cert.pem -days 1 -nodes \
    -subj "/CN=test-rotation.local"

# Update .env to use new certificates
echo "SSL_CERT_PATH=./test-cert.pem" >> .env
echo "SSL_KEY_PATH=./test-key.pem" >> .env

# Regenerate config
./generate-config.sh

# Try starting with new certificates
docker-compose up -d

# Verify the new certificate is being used
docker-compose exec app openssl s_client -connect localhost:443 -showcerts < /dev/null 2>/dev/null | openssl x509 -noout -subject
# Should show: subject=CN = test-rotation.local

# Clean up
docker-compose down
rm test-cert.pem test-key.pem
```

### 7. Verify .gitignore

```bash
# Check .gitignore covers all sensitive files
cat .gitignore | grep -E "(\.env|\.pem|\.key|config\.json)"

# Verify git status doesn't show sensitive files
# Create test files
touch .env test.pem test.key meshcentral-data/config.json

git status
# None of these should appear in untracked files

# Clean up
rm .env test.pem test.key meshcentral-data/config.json
```

### 8. Test Production Deployment Configuration

```bash
# Test production docker-compose
docker-compose -f docker-compose.yml -f docker-compose.prod.yml config

# Verify production doesn't mount entire repo
docker-compose -f docker-compose.yml -f docker-compose.prod.yml config | grep -A 10 "volumes:"
# Should show selective mounts only:
# - ./package.json
# - ./package-lock.json
# - ./index.js
# - ./meshcentral-data
# NOT: - .:/app
```

### 9. Check for Credential References

```bash
# Search codebase for hardcoded credentials
grep -r -i "password\|api.key\|token" --include="*.js" --include="*.json" --include="*.py" . | \
    grep -v "example" | grep -v "template" | grep -v "node_modules"
# Review output - should only show variable names, not actual values

# Check for email addresses
grep -r -oE "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}" . \
    --exclude-dir=node_modules --exclude-dir=.git | \
    grep -v "example.com" | grep -v "@users.noreply.github.com"
# Review output - should only show placeholder emails
```

### 10. Validate with Security Tools

```bash
# Run npm audit
npm audit --audit-level=high

# If you have GitHub CLI, test the security workflow
gh workflow run security-scan.yml

# Check workflow status
gh run list --workflow=security-scan.yml
```

## Verification Checklist

After running tests, verify:

- [ ] No .env files in git (`git ls-files | grep '\.env$'` returns nothing)
- [ ] No certificate files in git (`git ls-files | grep -E '\.(pem|key|crt)$'` returns nothing)
- [ ] No secrets in git history (`git log -p --all | grep "PRIVATE KEY"` returns nothing)
- [ ] .gitignore properly configured (includes .env, *.pem, *.key, config.json)
- [ ] Pre-commit hook installed and working
- [ ] Fresh clone can deploy with new .env file
- [ ] Configuration generation works (`./generate-config.sh` succeeds)
- [ ] Docker compose validates (`docker-compose config` succeeds)
- [ ] Application starts with environment variables only
- [ ] New certificates work (old certs not required)
- [ ] Production docker-compose uses selective mounts
- [ ] No hardcoded credentials in source code

## If Tests Fail

### Found secrets in git history?
See [MIGRATION.md](MIGRATION.md) section "Step 7: Clean Committed Secrets"

### Found committed certificate files?
```bash
# Remove from git (keep local copy)
git rm --cached *.pem *.key *.crt
git commit -m "Remove certificate files from version control"

# Add to .gitignore if not already there
echo "*.pem" >> .gitignore
echo "*.key" >> .gitignore
echo "*.crt" >> .gitignore
```

### Application won't start without old secrets?
This indicates hardcoded dependencies on old secrets:
1. Review error logs: `docker-compose logs`
2. Check for hardcoded paths or values
3. Update to use environment variables
4. Regenerate all secrets/certificates

## Success Criteria

Your secret rotation is successful when:

1. A fresh clone works with only `.env.example` → `.env` + new values
2. No historical secrets needed to run the application
3. All secrets in environment variables only
4. Pre-commit hook prevents new secret commits
5. Security scans pass (TruffleHog, npm audit, file scan)

## Post-Rotation Actions

After successful testing:

1. **Revoke old certificates** (if using custom certs)
2. **Update deployed environments** with new secrets
3. **Notify team members** of the rotation
4. **Document** which secrets were rotated and when
5. **Monitor** logs for any issues using old credentials
6. **Update** password managers with new credentials

## Questions?

See:
- [SECURITY.md](SECURITY.md) - Security best practices
- [MIGRATION.md](MIGRATION.md) - Migration guide
- [README.md](README.md) - General documentation
