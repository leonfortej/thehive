# Cortex Integration Guide

This guide explains how to connect this GitHub repository to your Cortex instance with automatic updates.

## Architecture Overview

- **GitHub Repository**: This repo contains custom analyzers and responders
- **Docker Host**: Where your TheHive and Cortex containers run
- **Auto-Sync**: Cron job pulls updates from GitHub on a regular schedule
- **Volume Mount**: Repository directory is mounted into Cortex container

## Prerequisites

- Docker and Docker Compose installed
- TheHive and Cortex running in Docker
- SSH access to the Docker host
- Git installed on the Docker host

## Setup Instructions

### Step 1: Clone Repository on Docker Host

On your Docker host (not Windows), clone this repository:

```bash
# SSH into your Docker host
ssh user@your-docker-host

# Clone the repository
cd /opt
sudo git clone https://github.com/YOUR_ORG/thehive.git CustomAnalyzers

# Set proper ownership (adjust if Cortex runs as different user)
sudo chown -R cortex:cortex /opt/CustomAnalyzers

# Or if running as root in Docker:
sudo chown -R root:root /opt/CustomAnalyzers
```

### Step 2: Configure Cortex

Create or update your Cortex configuration file on the Docker host:

```bash
# Create custom application.conf
sudo nano /opt/cortex/application.conf
```

Add the following configuration:

```hocon
# Custom Analyzers and Responders Configuration
analyzer {
  urls = [
    # Official StrangeBee catalog (for Docker-based analyzers)
    "https://catalogs.download.strangebee.com/latest/json/analyzers.json",

    # Your custom analyzers (file-based)
    "/opt/CustomAnalyzers/analyzers"
  ]
}

responder {
  urls = [
    # Official StrangeBee catalog (for Docker-based responders)
    "https://catalogs.download.strangebee.com/latest/json/responders.json",

    # Your custom responders (file-based)
    "/opt/CustomAnalyzers/responders"
  ]
}
```

### Step 3: Update Docker Compose

Update your `docker-compose.yml` to mount the repository and custom config:

```yaml
services:
  cortex:
    image: strangebee/cortex:latest
    volumes:
      # Docker socket for running analyzers/responders in containers
      - /var/run/docker.sock:/var/run/docker.sock

      # Job files directory
      - cortex-jobs:/tmp/cortex-jobs

      # Custom analyzers and responders (read-only)
      - /opt/CustomAnalyzers:/opt/CustomAnalyzers:ro

      # Custom configuration
      - /opt/cortex/application.conf:/etc/cortex/application.conf:ro

    environment:
      - job_directory=/tmp/cortex-jobs
      - docker_job_directory=/var/run/cortex/jobs
    ports:
      - "9001:9001"
    # ... rest of your configuration

volumes:
  cortex-jobs:
```

Restart Cortex to apply changes:

```bash
docker-compose restart cortex
```

### Step 4: Deploy Auto-Update Script

Copy the update script to the Docker host:

```bash
# Create scripts directory
sudo mkdir -p /opt/scripts

# Copy the script (you'll need to transfer this from the repo)
sudo cp scripts/update-cortex-analyzers.sh /opt/scripts/

# Make it executable
sudo chmod +x /opt/scripts/update-cortex-analyzers.sh

# Update the REPO_DIR in the script if needed
sudo nano /opt/scripts/update-cortex-analyzers.sh
# Set: REPO_DIR="/opt/CustomAnalyzers"
```

### Step 5: (Optional) Configure Cortex API for Automatic Refresh

If you want the script to automatically refresh Cortex after pulling updates:

1. **Generate API Key in Cortex:**
   - Log into Cortex web UI
   - Go to Organization settings
   - Create a new API key with appropriate permissions

2. **Add API Key to Script:**
   ```bash
   sudo nano /opt/scripts/update-cortex-analyzers.sh
   ```

   Update these lines:
   ```bash
   CORTEX_URL="http://cortex:9001"  # or http://localhost:9001 if on same host
   CORTEX_API_KEY="YOUR_API_KEY_HERE"
   ```

### Step 6: Set Up Cron Job

Create a cron job to run the update script regularly:

```bash
# Edit root crontab (or appropriate user)
sudo crontab -e
```

Add one of these schedules (choose based on your needs):

```bash
# Option 1: Every hour at minute 0
0 * * * * /opt/scripts/update-cortex-analyzers.sh

# Option 2: Every 30 minutes
*/30 * * * * /opt/scripts/update-cortex-analyzers.sh

# Option 3: Every 4 hours
0 */4 * * * /opt/scripts/update-cortex-analyzers.sh

# Option 4: Once daily at 3 AM
0 3 * * * /opt/scripts/update-cortex-analyzers.sh
```

### Step 7: (Optional) Configure Log Rotation

To prevent the log file from growing too large:

```bash
# Copy logrotate configuration
sudo cp scripts/cortex-sync-logrotate.conf /etc/logrotate.d/cortex-sync

# Test the configuration
sudo logrotate -d /etc/logrotate.d/cortex-sync
```

### Step 8: Test the Setup

Test the script manually first:

```bash
# Run the script manually
sudo /opt/scripts/update-cortex-analyzers.sh

# Check the log
sudo tail -f /var/log/cortex-sync.log

# Verify in Cortex UI
# Login to Cortex -> Organization Settings -> Analyzers
# You should see your custom analyzers listed
```

## Monitoring and Troubleshooting

### Check Sync Status

```bash
# View recent sync logs
sudo tail -50 /var/log/cortex-sync.log

# Check if cron job is running
sudo crontab -l

# View cron execution history
sudo grep CRON /var/log/syslog | grep update-cortex-analyzers
```

### Common Issues

**Issue: Analyzers not appearing in Cortex**
- Verify volume mount in Docker: `docker inspect cortex | grep -A 10 Mounts`
- Check file permissions: `ls -la /opt/CustomAnalyzers/analyzers`
- Check Cortex logs: `docker logs cortex`
- Try manual refresh in Cortex UI

**Issue: Git pull fails**
- Check SSH keys if using private repo: `sudo -u cortex ssh -T git@github.com`
- Verify repository path in script
- Check git status: `cd /opt/CustomAnalyzers && sudo git status`

**Issue: Script not running via cron**
- Check cron service: `sudo systemctl status cron`
- Verify script permissions: `ls -l /opt/scripts/update-cortex-analyzers.sh`
- Check for script errors: Run manually first

### Force Manual Refresh

If automatic refresh isn't working:

```bash
# Option 1: Restart Cortex
docker-compose restart cortex

# Option 2: Use Cortex UI
# Login as orgadmin -> Organization -> Click "Refresh Analyzers" button
```

## Update Schedule Recommendations

- **Development Environment**: Every 30 minutes or hourly
- **Testing Environment**: Every 4 hours
- **Production Environment**: Daily (off-peak hours)

## Security Considerations

1. **File Permissions**: Ensure repository is read-only for Cortex container
2. **API Keys**: Store API keys securely, use environment variables if possible
3. **Git Authentication**: Use SSH keys or deploy keys for private repositories
4. **Log Files**: Rotate logs to prevent disk space issues

## Next Steps

1. Add more custom analyzers to the `analyzers/` directory
2. Add responders to the `responders/` directory
3. Push changes to GitHub
4. Wait for next sync cycle or run script manually
5. Refresh Cortex UI to see new analyzers/responders

## Additional Resources

- [Cortex Documentation](https://docs.strangebee.com/cortex/)
- [Custom Analyzer Development](https://thehive-project.github.io/Cortex-Analyzers/dev_guides/)
- [TheHive Project GitHub](https://github.com/TheHive-Project/Cortex-Analyzers)
