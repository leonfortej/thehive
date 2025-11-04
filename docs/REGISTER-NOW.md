# 🚀 Register Templates NOW - Complete Guide

## What You're About to Do

You'll register two HTML templates in TheHive 5 that will transform the raw JSON output into beautiful, formatted reports with colored taxonomy cards.

**Time Required:** 5 minutes
**Difficulty:** Easy (copy & paste)

---

## 🎯 Step 1: Access Platform Management

1. Open TheHive in your browser: **http://localhost:9000**
2. **Log in as administrator** (required for template management)
3. Click your **profile icon** (top-right corner)
4. Select **"Platform Management"**
5. In left sidebar, click **"Analyzer Templates"**
6. Click **"+ Create Analyzer Template"** button

---

## 📝 Step 2: Fill in Basic Information

**Copy and paste these EXACT values:**

### Field: Analyzer Name
```
UserLogonHistory_BSCustom_1_0_0
```
⚠️ **CRITICAL**: Must match exactly! Underscores and version matter!

### Field: Analyzer ID
```
9731cf796e771b34027230f77877a14c
```

### Field: Name
```
UserLogonHistory_BSCustom
```

### Field: Version
```
1.0.0
```

---

## 📋 Step 3: Short Report Template

**Open this file in Notepad:**
```
C:\thehive\analyzers\UserLogonHistory\templates\short.html
```

**Copy EVERYTHING** (Ctrl+A, Ctrl+C)

**Paste into** TheHive's **"Short Report Template"** field

**Should start with:**
```html
<span class="label"
      ng-repeat="t in content.taxonomies"
```

---

## 📋 Step 4: Long Report Template

**Open this file in Notepad:**
```
C:\thehive\analyzers\UserLogonHistory\templates\long.html
```

**Copy EVERYTHING** (Ctrl+A, Ctrl+C)

**Paste into** TheHive's **"Long Report Template"** field

**Should start with:**
```html
<div class="panel panel-info">
  <div class="panel-heading">
    <strong>User Login History Analysis</strong>
```

---

## 💾 Step 5: Save

1. **Double-check** all fields match exactly
2. Click **"Save"** or **"Create"** button
3. You should see success message
4. Template should appear in the list

---

## 🧪 Step 6: Test It!

### Run the Analyzer
1. Go back to TheHive main interface
2. Navigate to a **mail observable** (or create one)
3. Right-click → **Run Analyzers**
4. Select **UserLogonHistory_BSCustom**
5. Wait 30-60 seconds for completion

### View Results
1. Click on the completed job
2. **Hard refresh browser:** Press **Ctrl + F5**
3. Look for the report

---

## ✅ Success Indicators

**You should see:**

### Top Section
**10 colored taxonomy cards in a row:**
- 🔵 Account: jason.leonforte@brightspeed.com
- 🟡 RiskLevel: Medium
- 🔵 TotalSignins: 99
- 🟢 SuccessfulSignins: 93
- 🔴 FailedSignins: 6
- 🔵 UniqueIPs: 6
- 🔵 UniqueLocations: 2
- 🔵 UniqueDevices: 7
- 🟢 MFAUsage: 40%
- 🟢 HighRiskSignins: 0

### Report Section
**Formatted report with:**
- ✅ Account info section with risk badge
- ✅ Summary metrics in colored panels
- ✅ Sortable IP address table
- ✅ Device list
- ✅ Geographic distribution
- ✅ Authentication details

### Artifacts Section
**IP addresses** listed as observables

**❌ If still seeing JSON:**
- Browser cache issue → Hard refresh (Ctrl+F5)
- Old analyzer run → Re-run the analyzer
- Name mismatch → Check analyzer name exactly matches

---

## 🐛 Troubleshooting

### Problem: Can't find "Platform Management"
**Solution:** You must be logged in as an **administrator**. Regular users can't access this.

### Problem: Can't find "Analyzer Templates"
**Solution:** Confirm you're on TheHive 5.x. Check version:
```bash
docker inspect thehive | grep -i THEHIVE_VERSION
```
TheHive 3/4 doesn't have this feature (uses old method).

### Problem: Saved but still seeing JSON
**Try these in order:**
1. **Hard refresh:** Ctrl + F5 (clears browser cache)
2. **Re-run analyzer** (don't view old cached results)
3. **Check name:** Must be exactly `UserLogonHistory_BSCustom_1_0_0`
4. **Clear browser cache completely**
5. **Log out and back in**

### Problem: Template shows errors when saving
**Check:**
- Copied **entire** template (including first tag)
- No extra spaces before/after
- No smart quotes (use plain text editor)
- No line break issues (copy from file, not this document)

---

## 📊 Before & After Comparison

### BEFORE (Current State) ❌
```json
{
  "account": "jason.leonforte@brightspeed.com",
  "summary_metrics": {
    "total_signins": 99,
    "successful_signins": 93,
    "failed_signins": 6
  },
  ...
}
```
**Analyst Experience:** "Ugh, I have to parse JSON to find key metrics?"

### AFTER (With Templates) ✅
**Top:**
[Account: jason...] [RiskLevel: Medium] [TotalSignins: 99] [SuccessfulSignins: 93] ...

**Report:**
[Clean formatted tables, colored risk badges, panels with metrics]

**Analyst Experience:** "Perfect! I can see everything at a glance!"

---

## 🎉 What This Achieves

**User Experience:**
- ⚡ **Faster Analysis**: Key metrics visible immediately
- 📊 **Visual Clarity**: Color-coded risk levels
- 🎯 **Actionable**: Click IPs to investigate further
- 📱 **Professional**: Formatted like enterprise tools
- 🔍 **Efficient**: No JSON parsing needed

**Technical Benefits:**
- ✅ Proper TheHive 5 integration
- ✅ Reusable across observables
- ✅ Customizable (edit templates anytime)
- ✅ Follows Cortex Analyzer best practices

---

## 📞 Need Help?

**Documentation:**
- Full guide: `C:\thehive\TEMPLATE-REGISTRATION-GUIDE.md`
- Quick steps: `C:\thehive\QUICK-REGISTRATION-STEPS.txt`
- Troubleshooting: `C:\thehive\analyzers\UserLogonHistory\NEXT-STEPS.md`

**Check Logs:**
```bash
docker logs cortex --tail 100
docker logs thehive --tail 100
```

**Verify Setup:**
```bash
# Check Cortex is running
docker ps | grep cortex

# Check analyzer image exists
docker images | grep userlogonhistory

# Check TheHive version
docker inspect thehive | grep -i version
```

---

## ⏱️ Time to Register!

**Current Status:**
- ✅ Clean analyzer code deployed
- ✅ Docker image rebuilt
- ✅ Cortex restarted
- ✅ Templates ready to copy
- ⏳ **Just need to register templates!**

**Next Action:** Follow Steps 1-6 above (5 minutes)

**After Registration:** Run analyzer and enjoy beautiful reports! 🎉

---

## 📁 File Locations Reference

| What | Where |
|------|-------|
| **Short template** | `C:\thehive\analyzers\UserLogonHistory\templates\short.html` |
| **Long template** | `C:\thehive\analyzers\UserLogonHistory\templates\long.html` |
| **Full guide** | `C:\thehive\TEMPLATE-REGISTRATION-GUIDE.md` |
| **Quick steps** | `C:\thehive\QUICK-REGISTRATION-STEPS.txt` |
| **This file** | `C:\thehive\REGISTER-NOW.md` |

---

**Ready? Let's do this! 🚀**

Open TheHive, follow the steps, and transform those JSON reports into something beautiful!
