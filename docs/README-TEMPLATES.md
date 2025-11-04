# UserLogonHistory Analyzer - Template Registration for TheHive 5

## Important: TheHive 5 Requires Manual Template Registration

Unlike TheHive 3/4, **TheHive 5 does not auto-discover templates** from the analyzer repository. Templates must be registered in TheHive's database through the UI or API.

## Why Are You Seeing JSON?

If you're seeing raw JSON instead of formatted reports and taxonomy cards, it's because the analyzer templates are not yet registered in TheHive 5.

## How to Register Templates

### Option 1: Manual Registration via UI (Recommended)

1. **Log into TheHive** as an administrator

2. **Navigate to Platform Management**
   - Click on your profile icon (top right)
   - Select "Platform Management"
   - Go to "Analyzer Templates"

3. **Create New Template**
   - Click "+ Create Analyzer Template"
   - Fill in the following fields:

   **Analyzer Name**: `UserLogonHistory_BSCustom_1_0_0`

   **Analyzer ID**: `9731cf796e771b34027230f77877a14c`

   **Name**: `UserLogonHistory_BSCustom`

   **Version**: `1.0.0`

   **Short Report Template**: Copy the contents from:
   ```
   C:\thehive\analyzers\UserLogonHistory\templates\short.html
   ```

   **Long Report Template**: Copy the contents from:
   ```
   C:\thehive\analyzers\UserLogonHistory\templates\long.html
   ```

4. **Save the Template**

5. **Test the Analyzer**
   - Run the analyzer again on a mail observable
   - You should now see:
     - **Taxonomy cards** at the top (10 colored summary cards)
     - **Formatted report** below (tables, panels, badges)
   - No more raw JSON!

### Option 2: API Registration (Requires API Key)

Run the PowerShell script with your TheHive API key:

```powershell
cd C:\thehive
.\Register-AnalyzerTemplate.ps1 -TheHiveUrl "http://your-thehive:9000" -ApiKey "your-api-key"
```

## What the Templates Do

### Short Template (short.html)
- Displays **10 taxonomy cards** at the top of the report
- Shows: Account, RiskLevel, TotalSignins, SuccessfulSignins, FailedSignins, UniqueIPs, UniqueLocations, UniqueDevices, MFAUsage, HighRiskSignins
- Color-coded by severity (blue=info, green=safe, yellow=suspicious, red=malicious)

### Long Template (long.html)
- Formats the full analysis data into a readable report
- Includes:
  - Account information with risk level badge
  - Summary metrics in panels
  - IP address table
  - Device list
  - Authentication details
  - Geographic distribution
  - Recent activity information

## Troubleshooting

**Still seeing JSON after registration?**
1. Hard refresh your browser (Ctrl+F5)
2. Check that the Analyzer Name matches exactly: `UserLogonHistory_BSCustom_1_0_0`
3. Verify the templates were saved correctly (no syntax errors)

**Can't find Analyzer Templates in Platform Management?**
- Make sure you're logged in as an administrator
- Check your TheHive version is 5.x: `docker inspect thehive | grep THEHIVE_VERSION`

## Why Can't Templates Be Bundled?

TheHive 5 changed the architecture to separate analyzer logic from presentation templates. This allows:
- Customizing templates without modifying analyzer code
- Using different templates for the same analyzer in different organizations
- Updating templates without rebuilding Docker images

Templates are stored in TheHive's database, not in the analyzer repository.
