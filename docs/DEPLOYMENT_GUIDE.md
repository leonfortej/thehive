# Deployment Guide

This guide covers deploying Cortex analyzers and responders to your TheHive/Cortex environment.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Deployment Methods](#deployment-methods)
3. [Local Deployment](#local-deployment)
4. [Docker Deployment](#docker-deployment)
5. [Configuration](#configuration)
6. [Verification](#verification)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **Operating System**: Linux (recommended), Windows, or macOS
- **Python**: 3.8 or higher
- **Cortex**: Version 3.x or higher
- **TheHive**: Version 4.x or 5.x

### Access Requirements

- SSH access to Cortex server (for local deployment)
- Docker access (for containerized deployment)
- Cortex admin credentials
- API endpoints and credentials for external services

## Deployment Methods

### Comparison

| Method | Pros | Cons | Use Case |
|--------|------|------|----------|
| **Local** | Simple, direct access | Manual dependency management | Development, small deployments |
| **Docker** | Isolated, portable, easy updates | Requires Docker knowledge | Production, multiple instances |

## Local Deployment

### Step 1: Prepare the Environment

```bash
# SSH to Cortex server
ssh user@cortex-server

# Navigate to analyzers directory
cd /opt/Cortex-Analyzers

# Or custom directory
cd /path/to/custom/analyzers
```

### Step 2: Clone or Copy Repository

```bash
# Option A: Clone from Git
git clone https://github.com/leonfortej/thehive.git
cd thehive

# Option B: Copy files via SCP
scp -r thehive/ user@cortex-server:/opt/Cortex-Analyzers/
```

### Step 3: Install Dependencies

```bash
# Install global dependencies
pip3 install -r requirements.txt

# Install analyzer-specific dependencies
cd analyzers/UserLogonHistory
pip3 install -r requirements.txt

# Make analyzer executable
chmod +x userlogonhistory.py
```

### Step 4: Configure Cortex Path

Edit Cortex configuration to include custom analyzers:

```bash
# Edit Cortex config
sudo nano /etc/cortex/application.conf
```

Add or update:
```hocon
analyzer {
  urls = [
    "https://download.thehive-project.org/analyzers.json"
    "file:///opt/Cortex-Analyzers/thehive/analyzers"
  ]
}
```

### Step 5: Restart Cortex

```bash
sudo systemctl restart cortex
```

### Step 6: Verify Installation

```bash
# Check Cortex logs
tail -f /var/log/cortex/application.log

# Verify analyzer is detected
curl -X GET http://localhost:9001/api/analyzer
```

## Docker Deployment

### Step 1: Build Docker Image

```bash
# Navigate to repository
cd thehive

# Build image for specific analyzer
docker build -t userlogonhistory:1.0 -f analyzers/UserLogonHistory/Dockerfile .

# Or build all analyzers
docker build -t thehive-analyzers:1.0 .
```

### Step 2: Test Docker Image

```bash
# Create test input
cat > test_input.json << EOF
{
  "data": "test@example.com",
  "dataType": "mail",
  "tlp": 2,
  "pap": 2,
  "config": {
    "api_url": "https://api.example.com/logon-history",
    "api_key": "test-key"
  }
}
EOF

# Run container with test input
docker run -i userlogonhistory:1.0 < test_input.json
```

### Step 3: Push to Registry (Optional)

```bash
# Tag for registry
docker tag userlogonhistory:1.0 registry.example.com/userlogonhistory:1.0

# Push to registry
docker push registry.example.com/userlogonhistory:1.0
```

### Step 4: Configure Cortex for Docker

Edit Cortex configuration:

```bash
sudo nano /etc/cortex/application.conf
```

Add Docker analyzer configuration:
```hocon
analyzer {
  urls = [
    "https://download.thehive-project.org/analyzers.json"
  ]

  docker {
    enable = true

    auto-update = false

    registry-auth {
      url = "registry.example.com"
      username = "user"
      password = "pass"
    }

    analyzers {
      UserLogonHistory {
        image = "registry.example.com/userlogonhistory:1.0"
      }
    }
  }
}
```

### Step 5: Restart Cortex

```bash
sudo systemctl restart cortex
```

## Configuration

### Analyzer Configuration in Cortex UI

1. **Log in to Cortex**
   - Navigate to Cortex web interface
   - Log in with admin credentials

2. **Navigate to Analyzers**
   - Go to Organization settings
   - Click "Analyzers" tab

3. **Find Your Analyzer**
   - Search for "UserLogonHistory"
   - Click the configuration icon

4. **Configure Parameters**
   ```
   api_url: https://api.example.com/v1/users/logon-history
   api_key: your-api-key-here
   timeout: 30
   verify_ssl: true
   ```

5. **Set TLP/PAP Restrictions**
   - Check "Enable TLP check"
   - Set max TLP to 2 (AMBER)
   - Check "Enable PAP check"
   - Set max PAP to 2 (AMBER)

6. **Save Configuration**

### Organization-Level vs Global Configuration

**Global Configuration** (all organizations):
```bash
# Edit in application.conf
analyzer.UserLogonHistory {
  api_url = "https://api.example.com/logon-history"
  timeout = 30
}
```

**Organization-Level** (specific organization):
- Configure via Cortex UI
- More flexible for multi-tenant deployments

### Environment Variables (Docker)

For Docker deployment, use environment variables:

```bash
docker run -i \
  -e API_URL="https://api.example.com/logon-history" \
  -e API_KEY="your-key" \
  userlogonhistory:1.0 < input.json
```

Update analyzer to read environment variables:
```python
import os
self.api_url = self.get_param('config.api_url', os.getenv('API_URL'))
```

## Verification

### Check Analyzer Registration

```bash
# Via API
curl -X GET http://localhost:9001/api/analyzer \
  -H "Authorization: Bearer YOUR_API_KEY"

# Check for UserLogonHistory in response
```

### Test Analyzer Execution

1. **From TheHive UI**
   - Open a case
   - Add mail observable
   - Run UserLogonHistory analyzer
   - Check results

2. **From Cortex API**
   ```bash
   curl -X POST http://localhost:9001/api/analyzer/UserLogonHistory/run \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "data": "test@example.com",
       "dataType": "mail",
       "tlp": 2,
       "pap": 2
     }'
   ```

3. **Check Job Status**
   ```bash
   curl -X GET http://localhost:9001/api/job/JOB_ID \
     -H "Authorization: Bearer YOUR_API_KEY"
   ```

### Monitor Logs

```bash
# Cortex logs
tail -f /var/log/cortex/application.log

# Analyzer-specific logs
tail -f /var/log/cortex/analyzers.log

# Docker logs (if using Docker)
docker logs -f container_id
```

## Troubleshooting

### Analyzer Not Appearing in Cortex

**Symptoms**: Analyzer doesn't show in Cortex UI

**Solutions**:
1. Check Cortex configuration path
2. Verify JSON file format
3. Restart Cortex service
4. Check file permissions
5. Review Cortex logs for errors

```bash
# Check analyzer path
ls -la /opt/Cortex-Analyzers/thehive/analyzers/UserLogonHistory/

# Validate JSON
python -m json.tool UserLogonHistory.json

# Check permissions
chmod +x userlogonhistory.py
chmod 644 UserLogonHistory.json

# Restart Cortex
sudo systemctl restart cortex
```

### Configuration Not Saving

**Symptoms**: Configuration changes don't persist

**Solutions**:
1. Check user permissions in Cortex
2. Verify organization settings
3. Clear browser cache
4. Check Cortex database

### Analyzer Execution Fails

**Symptoms**: Analyzer fails when run

**Solutions**:

1. **Check Dependencies**
   ```bash
   pip list | grep cortexutils
   pip list | grep requests
   ```

2. **Test Manually**
   ```bash
   echo '{"data":"test@example.com","dataType":"mail","tlp":2,"pap":2,"config":{"api_url":"..."}}' | \
     python userlogonhistory.py
   ```

3. **Check API Connectivity**
   ```bash
   curl -I https://api.example.com/logon-history
   ```

4. **Review Logs**
   ```bash
   grep -i "userlogon" /var/log/cortex/application.log
   ```

### Docker Issues

**Image Build Fails**:
```bash
# Clear Docker cache
docker builder prune

# Rebuild without cache
docker build --no-cache -t userlogonhistory:1.0 .
```

**Container Exits Immediately**:
```bash
# Check logs
docker logs container_id

# Run interactively
docker run -it userlogonhistory:1.0 /bin/bash
```

**Permission Errors**:
```bash
# Check file permissions in image
docker run -it userlogonhistory:1.0 ls -la /worker
```

### Performance Issues

**Slow Execution**:
1. Increase timeout parameter
2. Check network latency to API
3. Monitor resource usage
4. Enable caching if applicable

**High Memory Usage**:
1. Limit response size
2. Process data in chunks
3. Set Docker memory limits

```bash
# Run with memory limit
docker run -m 512m userlogonhistory:1.0
```

## Security Best Practices

### Credentials Management

1. **Never commit credentials**
   ```bash
   # Add to .gitignore
   echo "config.local.json" >> .gitignore
   echo "*.key" >> .gitignore
   ```

2. **Use environment variables**
   ```bash
   export API_KEY="your-key"
   ```

3. **Use secrets management**
   - HashiCorp Vault
   - AWS Secrets Manager
   - Azure Key Vault

### Network Security

1. **Use HTTPS** for all API calls
2. **Verify SSL certificates** in production
3. **Implement firewall rules**
4. **Use private networks** when possible

### Access Control

1. **Limit Cortex access** to authorized users
2. **Use API key authentication**
3. **Implement role-based access control**
4. **Audit analyzer usage**

## Updating Analyzers

### Local Deployment Update

```bash
# Pull latest changes
cd /opt/Cortex-Analyzers/thehive
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart Cortex
sudo systemctl restart cortex
```

### Docker Deployment Update

```bash
# Build new image
docker build -t userlogonhistory:1.1 .

# Update Cortex configuration
# Change image tag to :1.1

# Restart Cortex
sudo systemctl restart cortex

# Remove old image
docker rmi userlogonhistory:1.0
```

## Backup and Recovery

### Backup Configuration

```bash
# Backup Cortex config
cp /etc/cortex/application.conf /backup/application.conf.$(date +%Y%m%d)

# Backup analyzer directory
tar -czf /backup/analyzers-$(date +%Y%m%d).tar.gz /opt/Cortex-Analyzers/thehive
```

### Recovery

```bash
# Restore Cortex config
sudo cp /backup/application.conf.YYYYMMDD /etc/cortex/application.conf

# Restore analyzers
tar -xzf /backup/analyzers-YYYYMMDD.tar.gz -C /

# Restart Cortex
sudo systemctl restart cortex
```

## Monitoring and Maintenance

### Health Checks

```bash
# Check Cortex status
systemctl status cortex

# Check analyzer health
curl http://localhost:9001/api/health

# Monitor execution times
# Review job statistics in Cortex UI
```

### Log Rotation

Configure log rotation:
```bash
sudo nano /etc/logrotate.d/cortex
```

```
/var/log/cortex/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 640 cortex cortex
    sharedscripts
    postrotate
        systemctl reload cortex > /dev/null 2>&1 || true
    endscript
}
```

### Performance Monitoring

Monitor key metrics:
- Analyzer execution time
- API response time
- Error rates
- Resource usage (CPU, memory)

Use tools like:
- Prometheus + Grafana
- ELK Stack
- Datadog

## Support

For deployment issues:
- GitHub Issues: https://github.com/leonfortej/thehive/issues
- TheHive Community: https://community.thehive-project.org/
- Cortex Documentation: https://thehive-project.github.io/Cortex-Analyzers/

---
**Last Updated**: 2025-10-30
