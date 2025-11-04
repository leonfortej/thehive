# TheHive Custom Analyzers & Responders

**Custom Cortex analyzers for TheHive 5.x integration with Microsoft Sentinel and Azure services.**

## Overview

This repository contains production-ready Cortex analyzers designed for security operations workflows with TheHive. The analyzers provide deep integration with Microsoft Azure security services, particularly Microsoft Sentinel.

## Features

- **Modular Architecture**: Shared base framework for consistent analyzer development
- **Azure Integration**: Native integration with Microsoft Sentinel and Azure AD
- **Production Ready**: Comprehensive error handling, logging, and security controls
- **Docker Support**: Container-based deployment for easy scaling
- **TheHive 5.x Compatible**: Full support for TheHive 5.x report templates and taxonomies

## Available Analyzers

### UserLogonHistory
Analyzes Azure AD sign-in history for a user account over configurable time periods (default: 30 days).

**Features:**
- Comprehensive login analysis (success/failure rates, geographic distribution)
- Risk assessment with Microsoft Identity Protection integration
- Device and IP address tracking with first-time detection
- Detailed failed login analysis with anomaly highlighting
- MFA usage statistics
- Formatted HTML reports with TheHive templates

**Input:** Email address (mail observable)
**Output:** Risk taxonomies, detailed report, IP observables

[Read detailed documentation →](docs/README.md)

## Quick Start

### Prerequisites
- TheHive 5.x instance
- Cortex 3.x or built-in TheHive analyzers
- Docker and Docker Compose (for containerized deployment)
- Azure credentials with Log Analytics Reader permissions

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd 02-TheHive-Cortex
   ```

2. **Configure Docker deployment:**
   ```bash
   cd docker
   cp docker-compose.yml.example docker-compose.yml
   # Edit docker-compose.yml with your settings
   ```

3. **Deploy analyzers:**
   ```bash
   docker compose up -d
   ```

4. **Register in TheHive:**
   - Navigate to Organization Settings → Analyzer Templates
   - Import templates from `analyzers/UserLogonHistory/templates/`
   - Configure analyzer credentials in Cortex/TheHive

[Full deployment guide →](docs/DEPLOYMENT_GUIDE.md)

## Project Structure

```
02-TheHive-Cortex/
├── analyzers/
│   └── UserLogonHistory/        # User login analysis analyzer
│       ├── UserLogonHistory.json # Analyzer configuration
│       ├── userlogonhistory.py   # Main analyzer logic
│       ├── templates/            # TheHive report templates
│       ├── tests/                # Unit and integration tests
│       └── requirements.txt      # Python dependencies
│
├── common/                       # Shared framework
│   ├── base_analyzer.py          # Base analyzer class
│   ├── base_responder.py         # Base responder class
│   └── utils.py                  # Utility functions
│
├── docker/                       # Docker deployment configs
│   ├── docker-compose.yml        # Cortex + analyzers setup
│   └── Dockerfile                # Analyzer container build
│
└── docs/                         # Documentation
    ├── README.md                 # Main documentation
    ├── DEPLOYMENT_GUIDE.md       # Deployment instructions
    ├── DEVELOPMENT_GUIDE.md      # Analyzer development guide
    ├── CORTEX_INTEGRATION.md     # Cortex integration details
    └── TEMPLATE-REGISTRATION-GUIDE.md  # Template setup
```

## Documentation

- **[Main Documentation](docs/README.md)** - Complete analyzer documentation
- **[Deployment Guide](docs/DEPLOYMENT_GUIDE.md)** - Step-by-step deployment
- **[Development Guide](docs/DEVELOPMENT_GUIDE.md)** - Create custom analyzers
- **[Template Registration](docs/TEMPLATE-REGISTRATION-GUIDE.md)** - Setup TheHive templates
- **[Security Audit](docs/SECURITY_AUDIT.md)** - Security best practices
- **[Contributing](docs/CONTRIBUTING.md)** - Contribution guidelines

## Requirements

### Python Dependencies
- cortexutils >= 2.0
- requests >= 2.28.0
- azure-identity >= 1.12.0

### Azure Permissions
- **Log Analytics Reader** on Microsoft Sentinel workspace
- **Azure AD User Read** (for user queries)

### TheHive Requirements
- TheHive 5.x or later
- Cortex 3.x (or built-in analyzers)
- Network connectivity to Azure endpoints

## Configuration

### Analyzer Configuration
Edit `analyzers/UserLogonHistory/UserLogonHistory.json`:

```json
{
  "name": "UserLogonHistory_1_0",
  "version": "1.0",
  "author": "Security Operations Team",
  "license": "AGPL-V3",
  "dataTypeList": ["mail"],
  "config": {
    "check_tlp": true,
    "max_tlp": 2
  }
}
```

### Azure Authentication
Configure Azure credentials via:
- Environment variables (recommended for production)
- Managed Identity (for Azure-hosted deployments)
- Service Principal credentials

[Full configuration guide →](docs/DEPLOYMENT_GUIDE.md#configuration)

## Usage Examples

### From TheHive UI
1. Open a case with a mail observable (email address)
2. Click "Run Analyzer" on the observable
3. Select "UserLogonHistory_1_0"
4. Click "Run"
5. View formatted report in analyzer results

### Via Cortex API
```bash
curl -X POST http://cortex:9001/api/analyzer/<analyzer-id>/run \
  -H "Authorization: Bearer <api-key>" \
  -H "Content-Type: application/json" \
  -d '{
    "data": "user@example.com",
    "dataType": "mail",
    "tlp": 2,
    "pap": 2
  }'
```

## Development

### Creating a New Analyzer

1. Use the base framework:
   ```python
   from common.base_analyzer import BaseAnalyzer

   class MyAnalyzer(BaseAnalyzer):
       def run(self):
           data = self.get_data()
           # Your analysis logic
           self.report({'results': data})
   ```

2. Follow the development guide:
   [Development Guide →](docs/DEVELOPMENT_GUIDE.md)

### Running Tests
```bash
cd analyzers/UserLogonHistory
python -m pytest tests/
```

## Security Considerations

- **Credential Management**: Never commit credentials or API keys
- **TLP Enforcement**: Analyzers respect Traffic Light Protocol levels
- **Input Validation**: All inputs are validated before processing
- **Secure Communication**: TLS encryption for Azure API calls
- **Audit Logging**: Comprehensive logging for security audits

[Full security documentation →](docs/SECURITY_AUDIT.md)

## Troubleshooting

### Common Issues

**Analyzer not appearing in TheHive:**
- Verify analyzer JSON is valid
- Check Cortex logs: `docker logs cortex`
- Ensure dataTypeList matches observable type

**Azure authentication errors:**
- Verify credentials are configured correctly
- Check Azure RBAC permissions
- Ensure network connectivity to Azure endpoints

**Template not displaying:**
- Verify template name matches analyzer output
- Check template is imported in TheHive
- Review browser console for AngularJS errors

[Full troubleshooting guide →](docs/DEPLOYMENT_GUIDE.md#troubleshooting)

## Version History

**v1.0.0** (Current)
- UserLogonHistory analyzer with 30-day analysis
- Failed login tracking with first-time IP detection
- Risk assessment integration
- TheHive 5.x template support
- Docker deployment configuration

## Contributing

Contributions are welcome! Please read our [Contributing Guide](docs/CONTRIBUTING.md) for:
- Code style guidelines
- Testing requirements
- Pull request process
- Security reporting

## License

AGPL-V3 - See LICENSE file for details

## Support

For issues, questions, or contributions:
- Internal: Contact Security Operations Team
- Issues: File in your organization's issue tracker
- Documentation: See [docs/](docs/) directory

## Acknowledgments

Built with:
- [cortexutils](https://github.com/TheHive-Project/cortexutils) - Cortex analyzer framework
- [TheHive Project](https://thehive-project.org/) - Security incident response platform
- [Microsoft Azure](https://azure.microsoft.com/) - Cloud security services

---

**Last Updated:** November 4, 2025
**Maintained by:** Security Operations Team
**Repository:** Internal Security Tools
