# TheHive 5 - Template Registration Step-by-Step Guide

## Quick Copy-Paste Reference

**You'll need these values - have them ready:**

```
Analyzer Name: UserLogonHistory_BSCustom_1_0_0
Analyzer ID: 9731cf796e771b34027230f77877a14c
Name: UserLogonHistory_BSCustom
Version: 1.0.0
```

## Step-by-Step Instructions

### Step 1: Access TheHive
1. Open your web browser
2. Navigate to TheHive: `http://localhost:9000` (or your TheHive URL)
3. Log in as an **administrator** (templates can only be managed by admins)

### Step 2: Navigate to Analyzer Templates
1. Click your **profile icon** in the top-right corner
2. Select **"Platform Management"** from the dropdown
3. In the left sidebar, click **"Analyzer Templates"**

### Step 3: Create New Template
1. Click the **"+ Create Analyzer Template"** button (usually top-right)
2. A form will appear

### Step 4: Fill in Basic Information

**Copy and paste these exact values:**

**Field: Analyzer Name**
```
UserLogonHistory_BSCustom_1_0_0
```
⚠️ Must match exactly - including underscores and version!

**Field: Analyzer ID**
```
9731cf796e771b34027230f77877a14c
```
💡 This is the Cortex analyzer identifier

**Field: Name**
```
UserLogonHistory_BSCustom
```

**Field: Version**
```
1.0.0
```

### Step 5: Add Short Report Template

**Copy this entire template:**

```html
<span class="label"
      ng-repeat="t in content.taxonomies"
      ng-class="{'label-info': t.level=='info',
                 'label-success': t.level=='safe',
                 'label-warning': t.level=='suspicious',
                 'label-danger': t.level=='malicious'}">
  {{t.predicate}}: {{t.value}}
</span>
```

**Paste into:** "Short Report Template" field

**What this does:** Displays the 10 taxonomy cards at the top of the report with color coding.

### Step 6: Add Long Report Template

**Copy this entire template:**

```html
<div class="panel panel-info">
  <div class="panel-heading">
    <strong>User Login History Analysis</strong>
  </div>
  <div class="panel-body">

    <!-- Account Information -->
    <h4>Account Information</h4>
    <dl class="dl-horizontal">
      <dt>Account:</dt>
      <dd>{{content.account}}</dd>
      <dt>Analysis Period:</dt>
      <dd>{{content.analysis_period.start_date}} to {{content.analysis_period.end_date}}</dd>
      <dt>Report Generated:</dt>
      <dd>{{content.analysis_period.report_generated}}</dd>
      <dt>Overall Risk Level:</dt>
      <dd>
        <span class="label"
              ng-class="{'label-success': content.risk_assessment.overall_risk_level=='Low',
                         'label-warning': content.risk_assessment.overall_risk_level=='Medium',
                         'label-danger': content.risk_assessment.overall_risk_level=='High'}">
          {{content.risk_assessment.overall_risk_level}}
        </span>
      </dd>
    </dl>

    <!-- Summary Metrics -->
    <h4>Summary Metrics</h4>
    <div class="row">
      <div class="col-md-4">
        <div class="panel panel-default">
          <div class="panel-body text-center">
            <h3>{{content.summary_metrics.total_signins}}</h3>
            <p>Total Sign-ins</p>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="panel panel-success">
          <div class="panel-body text-center">
            <h3>{{content.summary_metrics.successful_signins}}</h3>
            <p>Successful</p>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="panel panel-danger">
          <div class="panel-body text-center">
            <h3>{{content.summary_metrics.failed_signins}}</h3>
            <p>Failed</p>
          </div>
        </div>
      </div>
    </div>

    <div class="row">
      <div class="col-md-4">
        <div class="panel panel-default">
          <div class="panel-body text-center">
            <h3>{{content.summary_metrics.unique_ip_addresses}}</h3>
            <p>Unique IP Addresses</p>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="panel panel-default">
          <div class="panel-body text-center">
            <h3>{{content.summary_metrics.unique_locations}}</h3>
            <p>Unique Locations</p>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="panel panel-default">
          <div class="panel-body text-center">
            <h3>{{content.summary_metrics.unique_devices}}</h3>
            <p>Unique Devices</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Authentication Details -->
    <h4>Authentication Details</h4>
    <dl class="dl-horizontal">
      <dt>MFA Usage:</dt>
      <dd>{{content.authentication_details.mfa_usage_percentage}}%</dd>
      <dt>Interactive Sign-ins:</dt>
      <dd>{{content.authentication_details.interactive_signins}}</dd>
      <dt>Non-Interactive Sign-ins:</dt>
      <dd>{{content.authentication_details.non_interactive_signins}}</dd>
      <dt>High-Risk Sign-ins:</dt>
      <dd>
        <span class="label"
              ng-class="{'label-success': content.authentication_details.high_risk_signins==0,
                         'label-danger': content.authentication_details.high_risk_signins>0}">
          {{content.authentication_details.high_risk_signins}}
        </span>
      </dd>
    </dl>

    <!-- Geographic Analysis -->
    <h4>Geographic Distribution</h4>
    <dl class="dl-horizontal">
      <dt>Countries:</dt>
      <dd>
        <span class="label label-info" ng-repeat="country in content.geographic_analysis.countries" style="margin-right: 5px;">
          {{country}}
        </span>
      </dd>
    </dl>

    <!-- IP Address Analysis -->
    <h4>Source IP Addresses</h4>
    <table class="table table-striped table-bordered">
      <thead>
        <tr>
          <th>IP Address</th>
          <th>Login Count</th>
        </tr>
      </thead>
      <tbody>
        <tr ng-repeat="ip in content.ip_address_analysis">
          <td>{{ip[0]}}</td>
          <td>{{ip[1]}}</td>
        </tr>
      </tbody>
    </table>

    <!-- Device Analysis -->
    <h4>Devices</h4>
    <ul>
      <li ng-repeat="device in content.device_analysis">{{device}}</li>
    </ul>

    <!-- Recent Activity -->
    <h4>Recent Activity</h4>
    <dl class="dl-horizontal">
      <dt>Events Captured:</dt>
      <dd>{{content.recent_activity.events_captured}}</dd>
      <dt>Query to View Details:</dt>
      <dd><code>{{content.recent_activity.query_to_view_details}}</code></dd>
    </dl>

    <!-- Anomalies -->
    <h4>Anomalies</h4>
    <p>{{content.anomalies.status}}</p>

  </div>
</div>
```

**Paste into:** "Long Report Template" field

**What this does:** Formats the full report with panels, tables, and color-coded risk indicators.

### Step 7: Save the Template
1. Review all fields to ensure values match exactly
2. Click **"Save"** or **"Create"** button
3. You should see a success message

## Verification

### After Saving
1. You should see the template listed in "Analyzer Templates"
2. Template name should show: `UserLogonHistory_BSCustom_1_0_0`
3. Status should be active/enabled

### Test It!
1. Go back to TheHive main interface
2. Find or create a **mail observable**
3. Right-click → **Run Analyzers** → Select **UserLogonHistory_BSCustom**
4. Wait for analysis to complete (~30-60 seconds)
5. View the report

## Expected Results After Registration

### Before Template Registration
```
Raw JSON displayed:
{
  "account": "user@example.com",
  "summary_metrics": {...},
  ...
}
```

### After Template Registration
**Top Section - 10 Colored Taxonomy Cards:**
- 🔵 Account: user@example.com
- 🟡 RiskLevel: Medium
- 🔵 TotalSignins: 99
- 🟢 SuccessfulSignins: 93
- 🔴 FailedSignins: 6
- 🔵 UniqueIPs: 6
- 🔵 UniqueLocations: 2
- 🔵 UniqueDevices: 7
- 🟢 MFAUsage: 40%
- 🟢 HighRiskSignins: 0

**Report Section - Formatted Data:**
- Account information with colored risk badge
- Summary metrics in colored panels
- Sortable IP address table
- Device list
- Geographic distribution
- Authentication details

## Troubleshooting

### "Can't find Platform Management"
**Solution:** Make sure you're logged in as an **administrator**. Regular users cannot access Platform Management.

### "Can't find Analyzer Templates"
**Solution:**
1. Ensure you're on TheHive 5.x (not 3.x or 4.x)
2. Check version: `docker inspect thehive | grep -i version`
3. TheHive 3/4 doesn't have this feature

### "Template saved but still seeing JSON"
**Solutions:**
1. **Hard refresh browser:** Press `Ctrl + F5` (Windows) or `Cmd + Shift + R` (Mac)
2. **Clear browser cache**
3. **Re-run the analyzer** (don't just view old results)
4. **Check analyzer name matches exactly:** `UserLogonHistory_BSCustom_1_0_0`

### "Analyzer not found in list"
**Solution:**
1. Check Cortex is running: `docker ps | grep cortex`
2. Verify analyzer is configured in Cortex
3. Check Cortex can connect to TheHive

### "Template shows errors"
**Solution:**
1. Verify you copied the **entire** template (including first `<span>` or `<div>` tag)
2. Check no extra characters were added
3. Ensure no smart quotes replaced regular quotes

## Quick Checklist

Before saving, verify:
- [ ] Analyzer Name: `UserLogonHistory_BSCustom_1_0_0` (exact match)
- [ ] Analyzer ID: `9731cf796e771b34027230f77877a14c`
- [ ] Short template: Starts with `<span class="label"`
- [ ] Long template: Starts with `<div class="panel panel-info">`
- [ ] Both templates copied completely
- [ ] No extra spaces or characters added
- [ ] Logged in as administrator

After saving, verify:
- [ ] Template appears in list
- [ ] Run analyzer on test observable
- [ ] Hard refresh browser (Ctrl+F5)
- [ ] Taxonomies appear as colored cards
- [ ] Report is formatted (not JSON)

## Success!

Once registered correctly, every time you run the UserLogonHistory analyzer, you'll see:
- ✅ Beautiful colored taxonomy cards
- ✅ Professional formatted report
- ✅ Sortable tables
- ✅ Color-coded risk indicators
- ✅ No more JSON!

This dramatically improves analyst workflow and report readability.
