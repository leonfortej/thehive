# UserLogonHistory Analyzer - Quick Start Guide

## Installation & Testing (5 Steps)

### Step 1: Install Dependencies

**On your Cortex server:**
```bash
cd /opt/CustomAnalyzers/analyzers/UserLogonHistory
pip3 install -r requirements.txt
```

**Verify:**
```bash
python3 -c "import cortexutils; print('✅ Installed:', cortexutils.__version__)"
```

---

### Step 2: Run Diagnostics

```bash
cd /opt/CustomAnalyzers/analyzers/UserLogonHistory
chmod +x test_diagnostics.sh
./test_diagnostics.sh
```

**Expected:** All checks should pass (✅)

**If any fail:** Follow the fix commands shown in the output

---

### Step 3: Test with Real API

**Create configuration:**
```bash
cd /opt/CustomAnalyzers/analyzers/UserLogonHistory

cat > test_input.json.local << 'EOF'
{
  "data": "your.email@example.com",
  "dataType": "mail",
  "tlp": 2,
  "pap": 2,
  "config": {
    "service": "UserLogonHistory_BSCustom",
    "api_url": "https://your-app.azurewebsites.net/api/Get-User-Logon-History-Report/triggers/manual/invoke?api-version=2022-05-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0",
    "api_signature": "your_signature_here",
    "timeout": 120,
    "verify_ssl": true
  }
}
EOF
```

**Edit the file:**
1. Replace `your.email@example.com` with real email
2. Replace `https://your-app.azurewebsites.net/...` with your Logic App URL (WITHOUT &sig=)
3. Replace `your_signature_here` with your signature key

**Run test:**
```bash
chmod +x test_with_real_api.sh
./test_with_real_api.sh
```

**Expected:** Should complete in 90-120 seconds and show success with taxonomies

---

### Step 4: Configure in Cortex

1. **Restart Cortex:**
   ```bash
   sudo systemctl restart cortex
   ```

2. **In Cortex Web UI:**
   - Navigate to **Organization → Analyzers**
   - Find **UserLogonHistory_BSCustom**
   - Click **Enable**
   - Configure:
     - `api_url`: Your Logic App URL WITHOUT &sig= at the end
     - `api_signature`: Your signature key
     - `timeout`: 120 (IMPORTANT!)
     - `verify_ssl`: true
   - Click **Save**

---

### Step 5: Test from TheHive

1. **Create test observable:**
   - Open TheHive
   - Create or open a case
   - Add observable:
     - Type: **mail**
     - Value: test email address
     - TLP: **2 (AMBER)**

2. **Run analyzer:**
   - Click **Run Analyzer**
   - Select **UserLogonHistory_BSCustom**
   - Click **Run**
   - Wait 90-120 seconds

3. **Check results:**
   - ✅ Status: Success
   - Taxonomies should appear (SignIns, Failed, RiskLevel, MFA)
   - Artifacts tab shows IP addresses
   - Full report shows in Reports tab

---

## Common Issues & Quick Fixes

| Issue | Quick Fix |
|-------|-----------|
| `ModuleNotFoundError: cortexutils` | `pip3 install cortexutils requests python-dateutil` |
| Timeout after 60 seconds | Set timeout to **120** in Cortex config |
| Connection refused | Check firewall: `curl -v https://azure.microsoft.com` |
| Invalid email format | Use valid email: `user@domain.com` |
| TLP exceeded | Use TLP 0, 1, or 2 (not 3) |
| Analyzer not visible in Cortex | Restart Cortex: `sudo systemctl restart cortex` |

---

## Testing Commands Cheat Sheet

```bash
# Quick diagnostic
cd /opt/CustomAnalyzers/analyzers/UserLogonHistory
./test_diagnostics.sh

# Test with real API
./test_with_real_api.sh

# Manual test with custom input
echo '{"data":"test@example.com","dataType":"mail","tlp":2,"pap":2,"config":{"service":"UserLogonHistory_BSCustom","api_url":"https://example.com","api_signature":"test","timeout":120}}' | python3 userlogonhistory.py

# Check Python packages
python3 -c "import cortexutils, requests, dateutil; print('All OK')"

# Validate JSON config
python3 -m json.tool UserLogonHistory.json

# Check Cortex logs
sudo tail -f /var/log/cortex/application.log

# Restart Cortex
sudo systemctl restart cortex
```

---

## Expected Performance

| Metric | Expected Value |
|--------|----------------|
| Execution time | 90-120 seconds |
| Timeout setting | 120 seconds |
| Success rate | >95% (with valid email) |
| Taxonomies | 4 (SignIns, Failed, RiskLevel, MFA) |
| Artifacts | Variable (IPs from logon history) |

---

## Configuration Reference

### Cortex Configuration
```
api_url: https://your-app.azurewebsites.net/api/Get-User-Logon-History-Report/triggers/manual/invoke?api-version=2022-05-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0

api_signature: AbCdEf123456... (DO NOT include &sig= prefix)

timeout: 120

verify_ssl: true
```

### TLP/PAP Limits
- Max TLP: 2 (AMBER)
- Max PAP: 2 (AMBER)

---

## Help & Troubleshooting

1. **Run diagnostics first:**
   ```bash
   ./test_diagnostics.sh
   ```

2. **Test with real API:**
   ```bash
   ./test_with_real_api.sh
   ```

3. **Check detailed guide:**
   - See `TROUBLESHOOTING_GUIDE.md` for comprehensive help

4. **Collect diagnostic info:**
   ```bash
   ./collect_diagnostics.sh > diagnostics.txt
   ```

---

## Success Checklist

Before declaring success, verify:

- [ ] All diagnostics pass (test_diagnostics.sh)
- [ ] Real API test succeeds (test_with_real_api.sh)
- [ ] Analyzer visible in Cortex UI
- [ ] Configuration saved in Cortex
- [ ] Test run from TheHive succeeds
- [ ] Taxonomies display correctly
- [ ] IP artifacts are created
- [ ] Execution time < 120 seconds

---

**Last Updated:** 2025-11-03
**Version:** 1.0.0
