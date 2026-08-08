# Backup and Restore Guide

## Overview

Regular backups ensure you can recover your XPanel configuration and user data in case of system failure or accidental deletion.

## What Gets Backed Up

The backup script saves:

1. **Database**: SQLite database file (or PostgreSQL dump)
2. **Environment**: Configuration including secrets and passwords
3. **Xray Config**: Generated proxy configurations
4. **Manifest**: Backup metadata and restore instructions

## Automatic Backups

### Setting Up Cron Jobs

For regular automatic backups, add a cron job:

```bash
# Edit crontab
sudo crontab -e

# Add daily backup at 2 AM
0 2 * * * /bin/bash /opt/xpanel/xpanel/installer/backup.sh

# Weekly backup on Sunday at 3 AM
0 3 * * 0 /bin/bash /opt/xpanel/xpanel/installer/backup.sh
```

### Backup Retention

Implement retention policy:

```bash
#!/bin/bash
# cleanup_old_backups.sh
BACKUP_DIR="/var/backups/xpanel"
DAYS_TO_KEEP=30

find $BACKUP_DIR -name "*.db" -mtime +$DAYS_TO_KEEP -delete
find $BACKUP_DIR -name "env_*" -mtime +$DAYS_TO_KEEP -delete
find $BACKUP_DIR -name "config_*.tar.gz" -mtime +$DAYS_TO_KEEP -delete
```

## Manual Backup

### Using the Script

```bash
sudo bash /opt/xpanel/xpanel/installer/backup.sh
```

Output:
```
Creating XPanel backup...
Backing up SQLite database...
Backing up environment configuration...
Backing up configuration files...

Backup completed successfully!
Backup location: /var/backups/xpanel

To restore:
  bash /opt/xpanel/xpanel/installer/restore.sh 20240101_120000
```

### Backup Location

Backups are stored in `/var/backups/xpanel/` by default.

### Backup Files

Each backup creates:
- `xpanel_YYYYMMDD_HHMMSS.db` - Database backup
- `env_YYYYMMDD_HHMMSS` - Environment variables
- `config_YYYYMMDD_HHMMSS.tar.gz` - Configuration files
- `manifest_YYYYMMDD_HHMMSS.txt` - Backup information

## Restoring from Backup

### List Available Backups

```bash
ls -la /var/backups/xpanel/
```

### Restore Process

1. **Stop XPanel**
   ```bash
   cd /opt/xpanel/xpanel/docker
   docker compose down
   ```

2. **Run Restore Script**
   ```bash
   sudo bash /opt/xpanel/xpanel/installer/restore.sh 20240101_120000
   ```

3. **Start XPanel**
   The restore script will automatically start the services.

### Manual Restore

If the script fails, restore manually:

```bash
# Stop services
docker compose down

# Restore database
cp /var/backups/xpanel/xpanel_20240101_120000.db \
   /opt/xpanel/xpanel/docker/xpanel_data/xpanel.db

# Restore environment
cp /var/backups/xpanel/env_20240101_120000 \
   /opt/xpanel/xpanel/docker/.env

# Restore config
tar -xzf /var/backups/xpanel/config_20240101_120000.tar.gz \
   -C /opt/xpanel/xpanel/docker/xpanel_config

# Start services
docker compose up -d
```

## PostgreSQL Backup

If using PostgreSQL, use pg_dump:

```bash
# Backup
docker exec xpanel-db pg_dump -U xpanel xpanel > backup.sql

# Restore
docker exec -i xpanel-db psql -U xpanel xpanel < backup.sql
```

Or use the built-in backup script which handles this automatically.

## Remote Backup Storage

### Copy to Remote Server

```bash
# After backup, copy to remote server
scp /var/backups/xpanel/* user@backup-server:/backups/xpanel/
```

### Cloud Storage

#### AWS S3
```bash
aws s3 cp /var/backups/xpanel/ s3://your-bucket/xpanel-backups/ --recursive
```

#### Google Drive
```bash
rclone copy /var/backups/xpanel/ gdrive:xpanel-backups
```

## Disaster Recovery

### Full System Recovery

1. Install fresh OS on new server
2. Install Docker
3. Download XPanel installer
4. Restore from backup
5. Update DNS if IP changed

### Migration to New Server

```bash
# On old server
bash /opt/xpanel/xpanel/installer/backup.sh

# Copy backup to new server
scp /var/backups/xpanel/latest/* user@new-server:/tmp/xpanel-backup/

# On new server
# Install XPanel first
curl -fsSL https://raw.githubusercontent.com/yourusername/xpanel/main/installer/install.sh | bash

# Stop services
cd /opt/xpanel/xpanel/docker
docker compose down

# Restore
cp /tmp/xpanel-backup/*.db ./xpanel_data/
cp /tmp/xpanel-backup/env_* ./.env
tar -xzf /tmp/xpanel-backup/config_*.tar.gz -C ./xpanel_config/

# Start
docker compose up -d
```

## Verification

After restore, verify:

1. **Login to panel**: Check admin access works
2. **User list**: Verify all users are present
3. **Configurations**: Test a few subscription links
4. **Traffic data**: Check historical usage is intact

## Troubleshooting

### Backup Fails

Check permissions:
```bash
sudo chown -R root:root /var/backups/xpanel
sudo chmod 755 /var/backups/xpanel
```

Check disk space:
```bash
df -h /var/backups
```

### Restore Fails

Verify backup integrity:
```bash
# Check database file
sqlite3 /var/backups/xpanel/xpanel_*.db ".tables"

# Check tar archive
tar -tzf /var/backups/xpanel/config_*.tar.gz
```

Check logs:
```bash
docker logs xpanel
```

## Best Practices

1. **Regular Schedule**: Daily or weekly backups
2. **Multiple Copies**: Keep local and remote backups
3. **Test Restores**: Periodically test restoration process
4. **Secure Storage**: Encrypt sensitive backups
5. **Version Control**: Keep multiple backup versions
6. **Documentation**: Maintain backup logs

---

⚠️ **IMPORTANT**: Always verify backups are working before relying on them for disaster recovery.

⚠️ **LEGAL DISCLAIMER**: Use responsibly and in compliance with all applicable laws.
