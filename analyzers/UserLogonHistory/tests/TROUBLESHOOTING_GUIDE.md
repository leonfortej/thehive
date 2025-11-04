# UserLogonHistory Analyzer - Troubleshooting Guide

## Quick Reference

This guide provides step-by-step troubleshooting for the UserLogonHistory analyzer deployment on Cortex.

---

## Step 1: Verify Python Dependencies

### Check if cortexutils is installed

```bash
# On your Cortex server
python3 -c "import cortexutils; print('SUCCESS: cortexutils version:', cortexutils.__version__)"
```

**Expected Output:**
```
SUCCESS: cortexutils version: 2.2.1
```

**If you get an error:**
```bash
# Install dependencies
cd /opt/CustomAnalyzers/analyzers/UserLogonHistory
pip3 install -r requirements.txt

# Or if running as cortex user:
sudo -u cortex pip3 install -r requirements.txt
```

### Verify all required packages

```bash
python3 -c "
import cortexutils
import requests
import dateutil
print('All packages imported successfully!')
print('cortexutils:', cortexutils.__version__)
print('requests:', requests.__version__)
print('dateutil:', dateutil.__version__)
"
```

---

## Step 2: Test Basic Analyzer Loading

### Test if the analyzer script can be executed

```bash
cd /opt/CustomAnalyzers/analyzers/UserLogonHistory

# Test basic import
python3 -c "
import sys
sys.path.insert(0, '/opt/CustomAnalyzers')
from common.base_analyzer import BaseAnalyzer
from common.utils import APIClient, DataValidator
print('Base modules loaded successfully!')
"
```

**Expected Output:**
```
Base modules loaded successfully!
```

**Common Errors:**

1. **ModuleNotFoundError: No module named 'cortexutils'**
   - Solution: Install cortexutils (see Step 1)

2. **ModuleNotFoundError: No module named 'common'**
   - Solution: Ensure `/opt/CustomAnalyzers/common/` directory exists
   - Verify common module files are present

3. **Permission denied**
   - Solution: Check file permissions
   ```bash
   chmod +x userlogonhistory.py
   chown -R cortex:cortex /opt/CustomAnalyzers
   ```

---

## Step 3: Test with Sample Input

### Create a test input file

```bash
cd /opt/CustomAnalyzers/analyzers/UserLogonHistory

cat > test_basic.json << 'EOF'
{
  "data": "test.user@example.com",
  "dataType": "mail",
  "tlp": 2,
  "pap": 2,
  "config": {
    "service": "UserLogonHistory_BSCustom",
    "api_url": "https://example.com/api",
    "api_signature": "test_signature_key",
    "timeout": 60,
    "verify_ssl": true
  }
}
EOF
```

### Test the analyzer

```bash
cat test_basic.json | python3 userlogonhistory.py
```

**Expected Output (for test/invalid endpoint):**
```json
{
  "success": false,
  "errorMessage": "Failed to retrieve logon history: ..."
}
```

**This is NORMAL** - we're just testing that the analyzer loads and processes input correctly.

**What we're checking:**
- ✅ Analyzer accepts input
- ✅ Parses configuration
- ✅ Validates email format
- ✅ Attempts API connection (will fail with test endpoint)

**Common Errors:**

1. **"Invalid email format"**
   - Expected if you use invalid email
   - Change to valid format: `user@domain.com`

2. **"API URL is required"**
   - Add api_url to config section

3. **"TLP level 3 exceeds maximum allowed level 2"**
   - Reduce tlp to 0, 1, or 2

---

## Step 4: Test with Real API Endpoint

### Create test file with your real configuration

```bash
cat > test_real.json << 'EOF'
{
  "data": "YOUR_TEST_EMAIL@example.com",
  "dataType": "mail",
  "tlp": 2,
  "pap": 2,
  "config": {
    "service": "UserLogonHistory_BSCustom",
    "api_url": "YOUR_AZURE_LOGIC_APP_URL_WITHOUT_SIG",
    "api_signature": "YOUR_API_SIGNATURE",
    "timeout": 120,
    "verify_ssl": true
  }
}
EOF

# Make sure to replace:
# - YOUR_TEST_EMAIL@example.com with real email
# - YOUR_AZURE_LOGIC_APP_URL_WITHOUT_SIG with your Logic App URL (without &sig=)
# - YOUR_API_SIGNATURE with your signature key
```

### Run the test

```bash
# Run and save output
cat test_real.json | python3 userlogonhistory.py 2>&1 | tee test_output.json

# Check if successful
cat test_output.json | python3 -m json.tool
```

**Expected Successful Output:**
```json
{
  "success": true,
  "full": {
    "email": "user@example.com",
    "total_signins": 172,
    "successful_signins": 164,
    "failed_signins": 8,
    "unique_ips": 7,
    "risk_level": "Medium",
    "ip_addresses": [...]
  },
  "summary": {
    "taxonomies": [
      {
        "namespace": "LoginAnalysis",
        "predicate": "SignIns",
        "value": "172",
        "level": "info"
      },
      ...
    ]
  },
  "artifacts": [
    {
      "dataType": "ip",
      "data": "192.168.1.1",
      "message": "IP address from logon history..."
    }
  ]
}
```

**Common Errors:**

1. **Connection timeout (>60 seconds)**
   ```json
   {"success": false, "errorMessage": "Request timeout"}
   ```
   - **Solution**: Increase timeout to 120 seconds
   - Logic App queries take 90-120 seconds

2. **HTTP 401 Unauthorized**
   - Check api_signature is correct
   - Verify api_url matches your Logic App

3. **HTTP 400 Bad Request**
   - Logic App may not be receiving correct format
   - Check POST body format matches Logic App expectations

4. **Network/SSL errors**
   - Check firewall rules allow outbound HTTPS
   - Test network connectivity:
   ```bash
   curl -v "YOUR_LOGIC_APP_URL&sig=YOUR_SIGNATURE"
   ```

---

## Step 5: Verify Cortex Configuration

### Check analyzer appears in Cortex

1. Log into Cortex web UI
2. Navigate to **Organization → Analyzers**
3. Search for "UserLogonHistory_BSCustom"
4. Should appear in the list

**If not visible:**

```bash
# Restart Cortex
sudo systemctl restart cortex

# Check Cortex logs
sudo tail -f /var/log/cortex/application.log
```

### Configure the analyzer in Cortex UI

1. Click on **UserLogonHistory_BSCustom**
2. Click **Enable**
3. Configure parameters:
   - **api_url**: Your Logic App URL WITHOUT &sig= at the end
   - **api_signature**: Your signature key only
   - **timeout**: 120 (not 60!)
   - **verify_ssl**: true
4. Click **Save**

---

## Step 6: Test from TheHive

### Create test observable

1. Open TheHive
2. Create or open a case
3. Add observable:
   - **Type**: mail
   - **Value**: test email address
   - **TLP**: 2 (AMBER)
4. Click **Run Analyzer**
5. Select **UserLogonHistory_BSCustom**
6. Click **Run**

### Monitor execution

Watch for:
- ⏳ Status: "InProgress" (should take 90-120 seconds)
- ✅ Status: "Success"
- ❌ Status: "Failure"

### Check results

**If successful:**
- Taxonomies appear (SignIns, Failed, RiskLevel, MFA)
- Artifacts tab shows IP addresses
- Full report shows in Reports tab

**If failed:**
- Click on the failed job
- Check "Error Message"
- Copy full error for troubleshooting

---

## Step 7: Debug Common Issues

### Issue: "No module named 'cortexutils'"

**Diagnosis:**
```bash
# Check which Python Cortex uses
ps aux | grep cortex | grep python
# Note the Python path

# Test with that Python
/path/to/python -c "import cortexutils"
```

**Solution:**
```bash
# Install for correct Python version
/path/to/python -m pip install cortexutils requests python-dateutil
```

### Issue: "Timeout after 60 seconds"

**Diagnosis:**
- Logic App queries take 90-120 seconds
- Default timeout too short

**Solution:**
- In Cortex UI, set timeout to 120
- Or edit UserLogonHistory.json:
```json
{
  "name": "timeout",
  "defaultValue": 120
}
```

### Issue: "API returned success=false"

**Diagnosis:**
- Logic App received request but couldn't process it
- Email may not exist in your system
- Logic App encountered error

**Solution:**
1. Test email exists in your system
2. Check Logic App logs in Azure Portal
3. Verify Logic App is running
4. Test Logic App directly:
```bash
curl -X POST "YOUR_LOGIC_APP_URL&sig=YOUR_SIGNATURE" \
  -H "Content-Type: application/json" \
  -d '{"dataType":"mail","data":"test@example.com","tlp":2,"pap":2}'
```

### Issue: "Connection refused" or "Network unreachable"

**Diagnosis:**
- Cortex server can't reach Azure
- Firewall blocking outbound HTTPS
- DNS resolution issue

**Solution:**
```bash
# Test DNS resolution
nslookup your-app.azurewebsites.net

# Test network connectivity
curl -v https://your-app.azurewebsites.net

# Check firewall rules
sudo iptables -L -n | grep OUTPUT
```

### Issue: Missing taxonomies or artifacts

**Diagnosis:**
- Analyzer ran but didn't parse response correctly
- API response format changed

**Solution:**
1. Capture raw API response:
```bash
# Test manually and save response
cat test_real.json | python3 userlogonhistory.py 2>&1 | tee raw_output.json
```

2. Check if response has expected structure
3. Verify markdown parsing is working

---

## Step 8: Enable Debug Logging

### Modify analyzer for verbose logging

```bash
cd /opt/CustomAnalyzers/analyzers/UserLogonHistory

# Backup original
cp userlogonhistory.py userlogonhistory.py.backup

# Edit to increase logging (already has good logging)
```

### Check Cortex logs

```bash
# Follow Cortex logs in real-time
sudo tail -f /var/log/cortex/application.log

# Or check Cortex analyzer logs
sudo tail -f /var/log/cortex/analyzers.log

# Filter for UserLogonHistory
sudo grep -i "userlogon" /var/log/cortex/*.log
```

---

## Step 9: Validation Checklist

Use this checklist to verify everything is working:

### Pre-flight Checks
- [ ] Python 3.8+ installed
- [ ] cortexutils package installed
- [ ] requests package installed
- [ ] python-dateutil package installed
- [ ] Analyzer files in /opt/CustomAnalyzers/analyzers/UserLogonHistory/
- [ ] Common modules in /opt/CustomAnalyzers/common/
- [ ] Analyzer is executable (chmod +x)
- [ ] Correct file ownership (chown cortex:cortex)

### Configuration Checks
- [ ] Analyzer visible in Cortex UI
- [ ] Analyzer enabled in Cortex
- [ ] api_url configured (WITHOUT &sig= at the end)
- [ ] api_signature configured
- [ ] timeout set to 120 seconds
- [ ] verify_ssl set to true

### Network Checks
- [ ] Cortex server can reach Azure (curl test)
- [ ] DNS resolution working
- [ ] Firewall allows outbound HTTPS
- [ ] No proxy issues

### Functionality Checks
- [ ] Analyzer accepts input (manual test)
- [ ] Email validation working
- [ ] TLP/PAP validation working
- [ ] API connection successful
- [ ] Response parsing working
- [ ] Taxonomies generated
- [ ] Artifacts extracted

### Integration Checks
- [ ] Analyzer runs from TheHive
- [ ] Completes within 120 seconds
- [ ] Returns success status
- [ ] Taxonomies display in TheHive
- [ ] Artifacts clickable in TheHive
- [ ] Full report viewable

---

## Step 10: Getting Help

### Information to Collect

When asking for help, provide:

1. **Error message** (full text)
2. **Cortex version**: `cortex --version`
3. **Python version**: `python3 --version`
4. **Package versions**:
   ```bash
   pip3 list | grep -E "(cortexutils|requests|dateutil)"
   ```
5. **Analyzer test output**:
   ```bash
   cat test_basic.json | python3 userlogonhistory.py 2>&1
   ```
6. **Cortex logs** (last 50 lines):
   ```bash
   sudo tail -50 /var/log/cortex/application.log
   ```

### Common Solutions Summary

| Error | Solution |
|-------|----------|
| ModuleNotFoundError | Install Python packages |
| Timeout | Increase timeout to 120s |
| Connection refused | Check network/firewall |
| Invalid email format | Use valid email address |
| TLP exceeded | Use TLP 0-2 |
| API returned false | Check Logic App logs |
| Missing config | Configure in Cortex UI |

---

## Quick Test Script

Save this as `quick_test.sh`:

```bash
#!/bin/bash
echo "=== UserLogonHistory Analyzer Test ==="

echo -e "\n1. Checking Python packages..."
python3 -c "import cortexutils, requests, dateutil; print('✅ All packages installed')" || echo "❌ Missing packages"

echo -e "\n2. Testing analyzer import..."
cd /opt/CustomAnalyzers/analyzers/UserLogonHistory
python3 -c "from userlogonhistory import UserLogonHistoryAnalyzer; print('✅ Analyzer loads')" || echo "❌ Import failed"

echo -e "\n3. Testing with sample input..."
echo '{"data":"test@example.com","dataType":"mail","tlp":2,"pap":2,"config":{"service":"UserLogonHistory_BSCustom","api_url":"https://example.com","api_signature":"test","timeout":60}}' | python3 userlogonhistory.py 2>&1 | head -10

echo -e "\n=== Test Complete ==="
```

Run with:
```bash
chmod +x quick_test.sh
./quick_test.sh
```

---

**Last Updated**: 2025-11-03
