# UserLogonHistory Analyzer

## Overview

The UserLogonHistory analyzer retrieves user authentication history from a REST API endpoint. It provides comprehensive logon activity analysis including timestamps, IP addresses, geographic locations, and authentication status for security investigations and incident response.

## Purpose

This analyzer helps security analysts:
- Investigate suspicious user authentication patterns
- Track user logon activity across different locations and IP addresses
- Identify potential account compromise indicators
- Correlate authentication events during incident response
- Analyze authentication failures and brute force attempts

## Input Data Type

- **mail**: Email address of the user account

## Configuration Parameters

### Required Parameters

1. **api_url** (string)
   - Full URL of the REST API endpoint for retrieving logon history
   - Must include protocol (http:// or https://)
   - Example: `https://api.example.com/v1/users/logon-history`
   - The analyzer will append `?email={user_email}` as a query parameter

### Optional Parameters

2. **api_key** (string)
   - API key or bearer token for authentication
   - If provided, sent as `Authorization: Bearer {token}` header
   - Leave empty if API doesn't require authentication
   - Default: empty

3. **timeout** (number)
   - Request timeout in seconds
   - Default: 30

4. **verify_ssl** (boolean)
   - Whether to verify SSL certificates for HTTPS requests
   - Set to false for self-signed certificates (not recommended for production)
   - Default: true

## API Endpoint Requirements

Your REST API endpoint should:

1. **Accept GET requests** with email as a query parameter:
   ```
   GET https://api.example.com/v1/users/logon-history?email=user@example.com
   ```

2. **Return JSON response** with logon history data

3. **Support authentication** (if required) via Bearer token in Authorization header:
   ```
   Authorization: Bearer your-api-key-here
   ```

### Expected API Response Format

The analyzer is flexible and can handle multiple response formats. It looks for logon data in these fields (in order):
- `data`
- `logons`
- `events`
- `results`
- Direct array response

Each logon record should ideally include:
```json
{
  "timestamp": "2025-10-30T10:15:30Z",
  "ip_address": "192.168.1.100",
  "location": "New York, USA",
  "status": "success",
  "device": "Mozilla/5.0...",
  "city": "New York",
  "country": "USA"
}
```

**Supported field name variations:**
- Timestamp: `timestamp`, `login_time`, `datetime`
- IP Address: `ip_address`, `ip`, `source_ip`
- Location: `location`, `geo_location`
- Status: `status`, `result`
- Device: `device`, `user_agent`

### Example API Response Formats

**Format 1: Data wrapper**
```json
{
  "data": [
    {
      "timestamp": "2025-10-30T10:15:30Z",
      "ip_address": "192.168.1.100",
      "status": "success",
      "country": "USA"
    }
  ],
  "count": 1
}
```

**Format 2: Direct array**
```json
[
  {
    "login_time": "2025-10-30T10:15:30Z",
    "ip": "192.168.1.100",
    "result": "success"
  }
]
```

**Format 3: Events wrapper**
```json
{
  "events": [
    {
      "datetime": "2025-10-30T10:15:30Z",
      "source_ip": "192.168.1.100",
      "status": "failed"
    }
  ]
}
```

## Output

### Report Data

The analyzer returns:

```json
{
  "success": true,
  "email": "user@example.com",
  "logon_count": 15,
  "query_time": "2025-10-30T12:00:00Z",
  "logon_history": [
    {
      "timestamp": "2025-10-30T10:15:30Z",
      "ip_address": "192.168.1.100",
      "location": "New York, USA",
      "status": "success",
      "device": "Chrome/Windows",
      "city": "New York",
      "country": "USA"
    }
  ]
}
```

### Taxonomies

The analyzer generates three taxonomies:

1. **LogonCount**
   - Namespace: `UserLogonHistory`
   - Predicate: `LogonCount`
   - Value: Number of logon records
   - Level: `info`

2. **Status**
   - Namespace: `UserLogonHistory`
   - Predicate: `Status`
   - Value: `Retrieved` or `Failed`
   - Level: `safe` (success) or `suspicious` (failure)

3. **RiskLevel**
   - Namespace: `UserLogonHistory`
   - Predicate: `RiskLevel`
   - Value: `Low`, `Medium`, `High`, or `Unknown`
   - Level: `safe`, `suspicious`, or `malicious`

### Risk Assessment

Risk level is automatically calculated based on:
- **High Risk**: More than 5 failed logon attempts
- **Medium Risk**: 3-5 failed logon attempts OR logons from more than 3 countries
- **Low Risk**: Less than 3 failed logons and normal geographic patterns
- **Unknown**: No logon data available

### Artifacts

The analyzer extracts **IP addresses** from logon history as observables, allowing further investigation in TheHive.

## Installation

### Prerequisites

```bash
# Python 3.8 or higher
python --version

# Required packages
pip install -r requirements.txt
```

### Cortex Installation

1. Copy the analyzer directory to your Cortex analyzers path:
   ```bash
   cp -r UserLogonHistory /path/to/cortex/analyzers/
   ```

2. Install Python dependencies:
   ```bash
   cd /path/to/cortex/analyzers/UserLogonHistory
   pip install -r requirements.txt
   ```

3. Make the analyzer executable:
   ```bash
   chmod +x userlogonhistory.py
   ```

4. Configure the analyzer in Cortex UI:
   - Navigate to Organization → Analyzers
   - Find "UserLogonHistory" in the list
   - Click the configuration icon
   - Set the `api_url` parameter
   - Optionally set `api_key` if your API requires authentication
   - Adjust `timeout` and `verify_ssl` as needed
   - Save configuration

## Usage

### From TheHive

1. Open a case in TheHive
2. Add or select an observable of type "mail" (email address)
3. Click "Run Analyzer"
4. Select "UserLogonHistory"
5. Wait for analysis to complete
6. View results in the observable details

### Manual Testing

Test the analyzer with sample data:

```bash
# Create test input
echo '{
  "data": "user@example.com",
  "dataType": "mail",
  "tlp": 2,
  "pap": 2,
  "config": {
    "api_url": "https://api.example.com/v1/users/logon-history",
    "api_key": "your-api-key",
    "timeout": 30,
    "verify_ssl": true
  }
}' | python userlogonhistory.py
```

Expected output format:
```json
{
  "success": true,
  "artifacts": [...],
  "full": {...},
  "summary": {
    "taxonomies": [...]
  }
}
```

## Security Considerations

### TLP/PAP Restrictions

- **Maximum TLP**: 2 (AMBER) - Data may contain sensitive authentication information
- **Maximum PAP**: 2 (AMBER) - Limit automated actions on authentication data

### API Security

1. **Use HTTPS**: Always use encrypted connections to API endpoints
2. **Secure API Keys**: Store API keys securely in Cortex configuration
3. **SSL Verification**: Keep `verify_ssl` enabled in production
4. **Rate Limiting**: Be aware of API rate limits
5. **Data Privacy**: Ensure API complies with data privacy regulations

## Troubleshooting

### Common Issues

**1. "API URL is required" error**
- Configure the `api_url` parameter in Cortex
- Ensure URL includes protocol (https://)

**2. "Invalid email format" error**
- Verify the observable is type "mail"
- Check email address is valid format

**3. Connection timeout**
- Increase `timeout` parameter
- Check network connectivity to API
- Verify firewall rules allow outbound connections

**4. SSL certificate verification failed**
- For development/testing only: set `verify_ssl` to false
- For production: install proper SSL certificates

**5. Authentication failed**
- Verify `api_key` is correct
- Check API key has not expired
- Ensure API key has proper permissions

**6. Unknown API response structure**
- Check analyzer logs for warnings
- Verify API returns JSON format
- Ensure response includes logon data in expected fields

### Logging

The analyzer logs to stderr. To view logs:

```bash
# When running manually
python userlogonhistory.py 2> analyzer.log

# In Cortex, check Cortex logs:
tail -f /var/log/cortex/cortex.log
```

Log levels:
- **INFO**: Normal operations
- **WARNING**: Unexpected but handled situations
- **ERROR**: Failures requiring attention

## Customization

### Modifying API Response Processing

The `_process_response()` method in `userlogonhistory.py` handles different API response formats. To customize:

1. Edit the method to add your API's specific field names
2. Add new field mappings in the logon_entry dictionary
3. Update risk assessment logic if needed

### Custom Risk Assessment

The `_assess_risk()` method implements simple risk scoring. To enhance:

1. Add more sophisticated pattern detection
2. Implement machine learning models
3. Integrate with threat intelligence feeds
4. Add time-based anomaly detection

### Adding Custom Taxonomies

Override the `summary()` method to add custom taxonomies:

```python
def summary(self, raw):
    taxonomies = super().summary(raw)

    # Add custom taxonomy
    taxonomies['taxonomies'].append(
        self.build_taxonomy(
            namespace='UserLogonHistory',
            predicate='CustomMetric',
            value='CustomValue',
            level='info'
        )
    )

    return taxonomies
```

## Development

### Testing Changes

```bash
# Run with test data
cat test_input.json | python userlogonhistory.py

# Check output format
python -m json.tool output.json
```

### Code Style

- Follow PEP 8 guidelines
- Add docstrings to all methods
- Include type hints where appropriate
- Log important events

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/leonfortej/thehive/issues
- Documentation: https://github.com/leonfortej/thehive

## License

AGPL-V3

## Version History

### 1.0.0 (2025-10-30)
- Initial release
- REST API integration
- Email-based user lookup
- Multiple API response format support
- Automatic risk assessment
- IP address artifact extraction
- TLP/PAP validation

---
**Last Updated**: 2025-10-30
