# Security Guidelines for UserLogonHistory Analyzer

## Sensitive Data Protection

### What NOT to Commit to Git

**NEVER** commit the following to the repository:

1. **API Signatures/Keys**
   - Azure Logic App signature keys
   - API authentication tokens
   - Any access credentials

2. **Test Data with Real Information**
   - Actual user email addresses
   - Real API endpoints with credentials
   - Production URLs with embedded keys

3. **Test Files with Sensitive Data**
   - `test_input.json` (use `.example` version)
   - `*.local` files
   - Any `*Test.txt` or `*test.txt` files

### Protected Files

The `.gitignore` is configured to automatically exclude:
```
test_input.json.local
**/test_input.json
**/*Test.txt
**/*test.txt
*.key
*.pem
.env
config.local.json
secrets.json
```

### Safe Testing

1. **Use Example Files**
   - Copy `test_input.json.example` to `test_input.json.local`
   - Add your real credentials to the `.local` file
   - Never commit `.local` files

2. **Environment Variables** (Alternative)
   ```bash
   export API_URL="https://your-app.azurewebsites.net/..."
   export API_SIGNATURE="your-sig-here"
   ```

3. **Cortex Configuration**
   - Store credentials in Cortex UI configuration
   - Use Cortex's secure parameter storage
   - Credentials are encrypted by Cortex

## API Security

### Azure Logic App Security

1. **Signature Rotation**
   - Rotate API signatures regularly
   - Update Cortex configuration when rotated
   - Revoke old signatures immediately

2. **Access Control**
   - Limit Logic App to specific IP ranges if possible
   - Use Azure Private Links for enhanced security
   - Enable Azure AD authentication if available

3. **Monitoring**
   - Monitor Logic App access logs
   - Alert on unusual usage patterns
   - Track failed authentication attempts

### TLP/PAP Compliance

This analyzer enforces:
- **Maximum TLP: 2 (AMBER)** - Contains user authentication data
- **Maximum PAP: 2 (AMBER)** - Limit automated actions

**Why?**
- User login data is sensitive
- May contain PII (email, IP addresses)
- Should not be shared with external entities

## Data Handling

### What Data is Collected

The analyzer retrieves:
- Sign-in counts (total, successful, failed)
- IP addresses used for authentication
- Geographic locations
- Device information
- MFA usage statistics
- Risk assessment

### Data Storage

- **Cortex**: Stores analysis results in TheHive database
- **Retention**: Follow your organization's data retention policy
- **Artifacts**: IP addresses become observables for further investigation

### Data Minimization

The analyzer only extracts:
- Necessary authentication metrics
- IP addresses as observables
- Aggregated statistics

It does NOT extract:
- Full user session data
- Detailed device fingerprints
- Complete authentication tokens

## Incident Response Considerations

### When to Use This Analyzer

**Appropriate Use Cases:**
- Investigating compromised user accounts
- Analyzing suspicious login patterns
- Incident response for authentication anomalies
- Security audits and compliance checks

**Inappropriate Use Cases:**
- General user monitoring without justification
- Tracking user activity for non-security purposes
- Violating privacy policies or regulations

### Legal and Compliance

- Ensure use complies with:
  - GDPR (if applicable)
  - Corporate privacy policies
  - Employee monitoring regulations
  - Industry-specific compliance (HIPAA, PCI-DSS, etc.)

## Vulnerability Reporting

If you discover a security vulnerability:

1. **Do NOT** open a public GitHub issue
2. **Do NOT** share details publicly
3. **Email** the maintainers directly
4. **Include**:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if available)

## Best Practices

### For Developers

1. **Code Reviews**
   - Review for hardcoded credentials
   - Check for sensitive data in logs
   - Validate input sanitization

2. **Testing**
   - Use fake/example data for tests
   - Never use production credentials in tests
   - Clear test data after completion

3. **Documentation**
   - Mark sensitive parameters clearly
   - Provide security warnings where appropriate
   - Document data handling practices

### For Operators

1. **Deployment**
   - Use secure credential storage (HashiCorp Vault, Azure Key Vault)
   - Implement least privilege access
   - Audit analyzer usage regularly

2. **Monitoring**
   - Log analyzer executions
   - Alert on failures or anomalies
   - Track data access patterns

3. **Maintenance**
   - Keep dependencies updated
   - Apply security patches promptly
   - Review access logs regularly

## Contact

For security concerns:
- GitHub Repository: https://github.com/leonfortej/thehive
- Security Issues: (Contact maintainers directly)

---
**Last Updated**: 2025-10-30
**Version**: 2.0.0
