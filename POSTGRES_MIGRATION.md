# DaisyChain PostgreSQL Migration Guide

Complete guide for migrating DaisyChain (MeshCentral) from NeDB file-based storage to PostgreSQL database.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Migration Options](#migration-options)
4. [Local Testing (Recommended First)](#local-testing-recommended-first)
5. [Production Migration](#production-migration)
6. [Troubleshooting](#troubleshooting)
7. [Rollback Procedure](#rollback-procedure)
8. [FAQ](#faq)

---

## Overview

### Why Migrate to PostgreSQL?

- **Scalability**: Better performance for 100+ devices
- **Railway Integration**: Native backup, monitoring, and management
- **Reliability**: ACID compliance and robust backup features
- **DaisyChain Title Fix**: Fresh database picks up new branding immediately

### What Gets Migrated?

**Included:**
- User accounts and passwords
- Device registrations and groups
- Agent connection keys
- Event logs
- Power state history
- Statistics
- Custom scripts and settings

**Not Affected:**
- Agent certificates (stored separately in meshcentral-data/agentcerts/)
- Web certificates
- Agent connections (agents auto-reconnect)

### Migration Time

- **Database size**: ~96K (very small)
- **Expected downtime**: 15 minutes
- **Agent reconnection**: 2-3 minutes
- **Total project time**: 2-3 hours (including testing)

---

## Prerequisites

### Required

- Docker and Docker Compose installed
- Git repository access
- Backup of current meshcentral-data directory
- For Railway: PostgreSQL database provisioned

### Recommended

- Test in local environment first
- Schedule during low-traffic period
- Notify users of maintenance window

---

## Migration Options

### Option 1: Automated Migration (Recommended)

Use the provided migration script:

```bash
./migrate-to-postgres.sh
```

This script handles:
- Automatic backup
- NeDB export
- PostgreSQL configuration
- Data import
- Performance index creation
- Verification

### Option 2: Manual Migration

Follow the step-by-step guide below for full control.

---

## Local Testing (Recommended First)

### Step 1: Start Local PostgreSQL

```bash
# Start with local PostgreSQL
docker-compose -f docker-compose.yml -f docker-compose.postgres.yml up -d

# Verify PostgreSQL is running
docker-compose ps postgres
```

### Step 2: Export Current Data

```bash
# Stop services
docker-compose down

# Export NeDB to JSON
docker-compose run --rm meshcentral node node_modules/meshcentral --dbexport

# Verify export
ls -lh meshcentral-data/meshcentral.db.json
```

### Step 3: Regenerate Configuration

```bash
# Configuration already includes PostgreSQL settings
./generate-config.sh

# Verify postgres section exists
grep -A 5 '"postgres"' meshcentral-data/config.json
```

### Step 4: Start with PostgreSQL

```bash
# Start services
docker-compose -f docker-compose.yml -f docker-compose.postgres.yml up -d

# Watch logs
docker-compose logs -f meshcentral
```

Look for:
- "Connected to PostgreSQL database"
- "Database initialization complete"

### Step 5: Import Data

```bash
# Import data
docker-compose exec meshcentral node node_modules/meshcentral --dbimport

# Create performance index
docker-compose exec postgres psql -U postgres -d meshcentral \
  -c "CREATE INDEX idx_fkid ON eventids(fkid);"
```

### Step 6: Verify

```bash
# Run verification script
./verify-migration.sh

# Check database stats
docker-compose exec meshcentral node node_modules/meshcentral --dbstats

# Test web interface
open https://localhost
```

### Step 7: Test Functionality

1. Login with existing credentials
2. Verify device list
3. Wait for agents to reconnect (2-3 minutes)
4. Test remote desktop/terminal
5. Verify Goose AI scripts still work

---

## Production Migration

### Pre-Migration Checklist

- [ ] Local testing completed successfully
- [ ] Railway PostgreSQL provisioned
- [ ] Environment variables configured
- [ ] Backup created and verified
- [ ] Users notified (if applicable)
- [ ] Maintenance window scheduled

### Railway PostgreSQL Setup

1. **Provision PostgreSQL:**
   - In Railway dashboard, click "New" → "Database" → "Add PostgreSQL"
   - Note the connection details (Railway auto-provides environment variables)

2. **Verify Environment Variables:**
   ```bash
   railway variables
   ```

   Should include:
   - `PGHOST`
   - `PGPORT`
   - `PGUSER`
   - `PGPASSWORD`
   - `PGDATABASE`

3. **Create Performance Index:**
   ```bash
   # Connect to Railway PostgreSQL
   railway run psql

   # Create index
   CREATE INDEX idx_fkid ON eventids(fkid);
   ```

### Production Migration Steps

#### 1. Backup Current Production

```bash
# Create timestamped backup
mkdir -p ~/daisychain-backup-$(date +%Y%m%d-%H%M%S)
cp -r meshcentral-data ~/daisychain-backup-$(date +%Y%m%d-%H%M%S)/

# Export to JSON
docker-compose down
docker-compose run --rm meshcentral node node_modules/meshcentral --dbexport

# Copy export to backup
cp meshcentral-data/meshcentral.db.json ~/daisychain-backup-$(date +%Y%m%d-%H%M%S)/
```

#### 2. Update Repository

```bash
# Commit migration files (already done if following this guide)
git add meshcentral-data/config.json.template
git add docker-entrypoint.sh
git add .env.example
git add docker-compose.postgres.yml
git add migrate-to-postgres.sh
git add verify-migration.sh
git add POSTGRES_MIGRATION.md
git commit -m "Add PostgreSQL migration support"
git push origin main
```

#### 3. Deploy to Railway

```bash
# Railway will auto-deploy on push, or manually trigger:
railway up --service TreeTee

# Monitor deployment
railway logs --service TreeTee
```

#### 4. Import Data

```bash
# After deployment completes, import data
railway run --service TreeTee node node_modules/meshcentral --dbimport
```

#### 5. Verify Deployment

```bash
# Run verification
./verify-migration.sh

# Check web interface
curl -I https://tee.up.railway.app
```

#### 6. Monitor

- Check agent connections (should reconnect within 2-3 minutes)
- Monitor logs for errors
- Test remote control features
- Verify DaisyChain title displays correctly

---

## Troubleshooting

### PostgreSQL Connection Failed

**Symptoms:**
- "Unable to connect to PostgreSQL"
- Service restarts repeatedly

**Solutions:**
1. Verify PGHOST, PGPORT, PGUSER, PGPASSWORD are set
2. Check Railway PostgreSQL is running
3. Verify network connectivity
4. Review logs: `railway logs --service TreeTee`

### Import Failed

**Symptoms:**
- "Import failed" error
- Object count mismatch

**Solutions:**
1. Verify export JSON exists and is valid
2. Check PostgreSQL has enough storage
3. Ensure tables were created (restart once first)
4. Try manual import:
   ```bash
   railway run bash
   node node_modules/meshcentral --dbimport
   ```

### Agents Not Reconnecting

**Symptoms:**
- Devices show offline after 5+ minutes
- Agents report connection errors

**Solutions:**
1. Wait full 3 minutes (agents retry connection)
2. Check meshcentral.db has agent keys (should be preserved)
3. Verify certificates in meshcentral-data/agentcerts/
4. Review agent logs on client machines

### DaisyChain Title Still Shows TreeTee

**Symptoms:**
- Web interface shows "TreeTee" instead of "DaisyChain"

**Solutions:**
1. Fresh PostgreSQL database should pick up new title immediately
2. If not, check config.json has `"title": "DaisyChain"`
3. Clear browser cache (Ctrl+Shift+R)
4. Restart MeshCentral: `railway restart`

### Performance Issues

**Symptoms:**
- Slow queries
- Timeout errors
- Database growing rapidly

**Solutions:**
1. Create missing index:
   ```sql
   CREATE INDEX idx_fkid ON eventids(fkid);
   ```
2. Check database size: `railway run psql -c "\dt+"`
3. Review retention settings in config
4. Consider vacuuming: `VACUUM ANALYZE;`

---

## Rollback Procedure

If migration fails or issues arise, rollback to NeDB:

### Quick Rollback

```bash
# Stop services
docker-compose down

# Restore NeDB files from backup
cp ~/daisychain-backup-TIMESTAMP/meshcentral-data/*.db meshcentral-data/

# Remove postgres section from config
# Edit meshcentral-data/config.json.template:
# Delete or comment out the entire "postgres" section

# Regenerate config
./generate-config.sh

# Restart with NeDB
docker-compose up -d

# Verify
docker-compose logs -f meshcentral
```

### Railway Rollback

```bash
# Revert commit that added PostgreSQL
git revert HEAD
git push origin main

# Railway will auto-deploy the rollback

# Or manually rollback in Railway dashboard:
# 1. Go to Deployments tab
# 2. Find pre-migration deployment
# 3. Click "Redeploy"
```

**Rollback Time**: 5 minutes
**Data Loss**: None (if backup was properly maintained)

---

## FAQ

### Q: Will agents lose connection during migration?
**A**: Yes, briefly. Agents automatically reconnect within 2-3 minutes. No manual intervention needed.

### Q: Can I migrate without downtime?
**A**: No. Database migration requires stopping MeshCentral. However, downtime is minimal (15 minutes) with proper preparation.

### Q: What if I don't want to use PostgreSQL anymore?
**A**: Simply remove the "postgres" section from config.json.template and restart. MeshCentral will fall back to NeDB.

### Q: Does PostgreSQL cost extra on Railway?
**A**: Railway PostgreSQL has a free tier with limits. Check [Railway pricing](https://railway.app/pricing) for details.

### Q: Can I migrate from PostgreSQL back to NeDB?
**A**: Yes. Export from PostgreSQL, remove postgres config, restart, then import to NeDB. Same process in reverse.

### Q: Will my Let's Encrypt certificates be affected?
**A**: No. Certificates are stored separately in meshcentral-data directory, not in the database.

### Q: How do I backup PostgreSQL after migration?
**A**: Railway provides automatic backups. For manual backups:
```bash
railway run pg_dump meshcentral > backup.sql
```

### Q: What's the database size limit?
**A**: NeDB: ~100 devices. PostgreSQL: 1000s of devices (limited by Railway plan or your infrastructure).

### Q: Can I use MySQL instead of PostgreSQL?
**A**: Yes. MeshCentral supports MySQL, MariaDB, MongoDB, and PostgreSQL. This guide focuses on PostgreSQL due to Railway's native support.

---

## Additional Resources

- **MeshCentral Documentation**: https://ylianst.github.io/MeshCentral/
- **PostgreSQL Documentation**: https://www.postgresql.org/docs/
- **Railway Documentation**: https://docs.railway.app/
- **GitHub Issues**: Search "meshcentral postgresql" for community solutions

---

## Support

If you encounter issues not covered in this guide:

1. Check MeshCentral logs: `docker-compose logs meshcentral`
2. Review PostgreSQL logs: `railway logs --service TreeTee`
3. Run verification script: `./verify-migration.sh`
4. Search MeshCentral GitHub issues: https://github.com/Ylianst/MeshCentral/issues
5. Consult this project's issue tracker

---

## Change Log

- **2025-11-07**: Initial migration guide created
- Supports MeshCentral v1.1.42+
- PostgreSQL 15+ recommended
- Tested on Railway deployment platform

---

*This guide is maintained as part of the DaisyChain project. For updates, check the repository.*
