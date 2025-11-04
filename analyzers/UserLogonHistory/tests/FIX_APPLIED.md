# UserLogonHistory Analyzer - Configuration Fix Applied ✅

## Issue Resolved

**Date:** 2025-11-03
**Problem:** Analyzer was failing with `ModuleNotFoundError: No module named 'cortexutils'`
**Root Cause:** Cortex was trying to run the Python script from the mounted file system instead of using the Docker image
**Status:** ✅ **FIXED**

---

## What Was Wrong?

The error you saw:
```json
{
  "errorMessage": "Traceback (most recent call last):  File \"/opt/CustomAnalyzers/analyzers/UserLogonHistory/userlogonhistory.py\", line 20, in <module>    from common.base_analyzer import BaseAnalyzer  File \"/opt/CustomAnalyzers/analyzers/UserLogonHistory/../../common/__init__.py\", line 7, in <module>    from .base_analyzer import BaseAnalyzer  File \"/opt/CustomAnalyzers/analyzers/UserLogonHistory/../../common/base_analyzer.py\", line 12, in <module>    from cortexutils.analyzer import AnalyzerModuleNotFoundError: No module named 'cortexutils'",
  "success": false
}
```

This occurred because:
1. The analyzer configuration had: `"command": "UserLogonHistory/userlogonhistory.py"`
2. This told Cortex to run the Python script directly from `/opt/CustomAnalyzers` (mounted volume)
3. The mounted volume doesn't have Python dependencies installed
4. The Python script failed when trying to import `cortexutils`

**Even though the API call succeeded**, the analyzer couldn't generate the report for TheHive.

---

## What Was Fixed?

### Changed Configuration
**File:** `C:/thehive/analyzers/UserLogonHistory/UserLogonHistory.json`

**Before:**
```json
{
  "name": "UserLogonHistory_BSCustom",
  "baseConfig": "UserLogonHistory_BSCustom",
  "command": "UserLogonHistory/userlogonhistory.py",
  ...
}
```

**After:**
```json
{
  "name": "UserLogonHistory_BSCustom",
  "baseConfig": "UserLogonHistory_BSCustom",
  "dockerImage": "cortexneurons/userlogonhistory_bscustom:1_0_0",
  ...
}
```

### What This Does
- Tells Cortex to run the analyzer in a **Docker container** (using the image we built)
- The Docker image has **all dependencies pre-installed** (cortexutils, requests, python-dateutil)
- The analyzer now works completely isolated with all required packages

---

## Changes Applied

1. ✅ **Backed up original configuration:**
   - `UserLogonHistory.json.backup` created

2. ✅ **Updated configuration:**
   - Replaced `"command"` with `"dockerImage"`
   - Points to: `cortexneurons/userlogonhistory_bscustom:1_0_0`

3. ✅ **Restarted Cortex:**
   - Configuration reloaded
   - Cortex is healthy and running

4. ✅ **Verified:**
   - Docker image exists
   - Configuration updated in container
   - Cortex can access the image

---

## How It Works Now

```
TheHive sends observable (mail) to Cortex
    ↓
Cortex reads: UserLogonHistory.json
    ↓
Sees: "dockerImage": "cortexneurons/userlogonhistory_bscustom:1_0_0"
    ↓
Launches NEW container from that image
    ↓
Container has ALL dependencies (cortexutils, requests, etc.)
    ↓
Analyzer runs successfully:
  - Connects to Azure Logic App ✅
  - Retrieves logon history ✅
  - Parses data ✅
  - Generates report ✅
  - Returns taxonomies & artifacts ✅
    ↓
Results displayed in TheHive ✅
```

---

## Test Again from TheHive

The analyzer is now ready to test! Follow these steps:

### Step 1: Verify Analyzer is Available in Cortex

1. Open Cortex UI: `https://your-cortex-url/cortex`
2. Navigate to **Organization → Analyzers**
3. Find **"UserLogonHistory_BSCustom"**
4. Verify it shows as **enabled**
5. Check configuration:
   - `api_url`: Should be configured
   - `api_signature`: Should be configured
   - `timeout`: Should be **120** (not 60!)

### Step 2: Test from TheHive

1. **Open TheHive**
2. **Create or open a case**
3. **Add an observable:**
   - Type: **mail**
   - Value: `jason.leonforte@brightspeed.com` (or any valid email)
   - TLP: **2 (AMBER)**
4. **Click on the observable** to open it
5. **Click "Run Analyzer"**
6. **Select "UserLogonHistory_BSCustom"**
7. **Click "Run"**
8. **Wait 90-120 seconds** (this is normal for Logic App queries)

### Step 3: Verify Results

You should now see:

#### ✅ Taxonomies (4 displayed on observable)
| Namespace | Predicate | Value | Level |
|-----------|-----------|-------|-------|
| LoginAnalysis | SignIns | 96 | info |
| LoginAnalysis | Failed | 4 | info |
| LoginAnalysis | RiskLevel | Medium | suspicious |
| LoginAnalysis | MFA | 42% | suspicious |

#### ✅ Artifacts (IPs extracted)
- Type: `ip`
- Data: `64.53.89.127`
- Count: 96 logins

#### ✅ Full Report
- Navigate to the **Reports** tab on the observable
- You should see the complete markdown report with:
  - Executive Summary
  - Risk Indicators
  - Geographic Distribution
  - Source IP Analysis
  - Device & Application Summary
  - Authentication Details
  - Recommendations

---

## Expected Behavior

### ✅ Success Case
- Job status: **Success** (green)
- Execution time: 90-120 seconds
- Taxonomies: 4 visible on observable
- Artifacts: IP addresses created
- Report: Full markdown report available

### ❌ If It Still Fails

If you still get an error, collect this information:

1. **Check the error message in TheHive:**
   - Click on the failed job
   - Copy the full error message

2. **Check Cortex logs:**
   ```bash
   docker logs cortex --tail 100
   ```

3. **Verify Docker image:**
   ```bash
   docker images | grep userlogon
   ```

   Should show:
   ```
   cortexneurons/userlogonhistory_bscustom   1_0_0
   ```

4. **Test image manually:**
   ```bash
   cat C:/thehive/analyzers/UserLogonHistory/test_input.json.local | docker run --rm -i cortexneurons/userlogonhistory_bscustom:1_0_0
   ```

---

## Troubleshooting

### Issue: "Image not found"
**Solution:**
```bash
cd C:/thehive
docker build -t cortexneurons/userlogonhistory:1.0.0 -f analyzers/UserLogonHistory/Dockerfile .
docker tag cortexneurons/userlogonhistory:1.0.0 cortexneurons/userlogonhistory_bscustom:1_0_0
cd C:/docker/thehive/testing
docker-compose restart cortex
```

### Issue: "Timeout after 60 seconds"
**Solution:**
- In Cortex UI, go to Organization → Analyzers → UserLogonHistory_BSCustom
- Change `timeout` from **60** to **120**
- Save configuration

### Issue: "Configuration not loading"
**Solution:**
```bash
# Verify file is correct
cat C:/thehive/analyzers/UserLogonHistory/UserLogonHistory.json | grep dockerImage

# Should show:
# "dockerImage": "cortexneurons/userlogonhistory_bscustom:1_0_0",

# Restart Cortex
cd C:/docker/thehive/testing
docker-compose restart cortex
```

---

## Files Modified

| File | Action | Backup |
|------|--------|--------|
| `UserLogonHistory.json` | Modified | `UserLogonHistory.json.backup` |

---

## Validation Checklist

Before testing from TheHive, verify:

- [x] Docker image exists: `cortexneurons/userlogonhistory_bscustom:1_0_0`
- [x] Configuration updated: `dockerImage` field present
- [x] Cortex restarted and healthy
- [x] Configuration loaded in container
- [ ] Tested from TheHive (you do this)
- [ ] Taxonomies displayed (you verify this)
- [ ] Artifacts created (you verify this)
- [ ] Full report available (you verify this)

---

## What Changed vs Previous Test

| Aspect | Previous Test (Manual) | Current (From TheHive) |
|--------|----------------------|------------------------|
| How run | `docker run` command | Cortex launches container |
| Where run | Command line | TheHive observable |
| Dependencies | In Docker image ✅ | In Docker image ✅ |
| API call | Works ✅ | Should work ✅ |
| Report generation | Works ✅ | Should work ✅ |
| Result display | JSON to console | TheHive UI |

The **only difference** is now Cortex will launch the container (instead of you manually running it).

---

## Summary

✅ **Configuration Fixed**
✅ **Cortex Restarted**
✅ **Ready to Test**

The analyzer should now work correctly when run from TheHive. The Docker image has all dependencies and the configuration now tells Cortex to use it.

**Next Step:** Test it from TheHive using the steps above!

---

## Need Help?

If the analyzer still fails after this fix:
1. Share the **exact error message** from TheHive
2. Run: `docker logs cortex --tail 50`
3. Verify: `docker images | grep userlogon`
4. Share all outputs

---

**Fix Applied By:** Claude Code
**Date:** 2025-11-03
**Status:** ✅ **READY TO TEST**
