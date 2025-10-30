# TheHive Cortex Analyzers & Responders Framework

This repository contains custom Cortex analyzers and responders for TheHive integration, developed for StrangeBee TheHive SaaS platform.

## Project Structure

```
thehive/
├── analyzers/          # Custom Cortex analyzers
├── responders/         # Custom Cortex responders
├── common/             # Shared utilities and base classes
├── templates/          # HTML templates for report generation
├── docs/               # Additional documentation
└── README.md           # This file
```

## Overview

This framework provides a standardized structure for developing Cortex analyzers and responders with:

- **Reusable Base Classes**: Common functionality for all analyzers/responders
- **Utility Functions**: Shared helper methods for API calls, data processing, etc.
- **Template System**: Consistent report generation for TheHive UI
- **Documentation Standards**: Comprehensive documentation for each component

## Requirements

- Python 3.8+
- cortexutils library
- requests library

Install dependencies:
```bash
pip install -r requirements.txt
```

## Analyzers

Analyzers are automated tools that process observables from TheHive cases. Each analyzer:
- Accepts specific data types (IP, domain, email, file, etc.)
- Performs analysis via external APIs or internal logic
- Returns structured results with taxonomies for TheHive

### Current Analyzers

1. **UserLogonHistory**: Retrieves user logon history from REST API endpoints

## Responders

Responders are automated response actions that can be triggered from TheHive. Coming soon.

## Development Guide

### Creating a New Analyzer

1. Create a new directory under `analyzers/`
2. Implement your analyzer using the base class from `common/`
3. Create the service interaction JSON file with configuration
4. Add requirements.txt with dependencies
5. Create report templates in `templates/`
6. Document in the analyzer's README.md

### Service Interaction File Structure

Each analyzer requires a JSON configuration file:

```json
{
  "name": "AnalyzerName_Service",
  "version": "1.0.0",
  "author": "Your Name",
  "url": "https://github.com/leonfortej/thehive",
  "license": "AGPL-V3",
  "description": "Description of the analyzer",
  "dataTypeList": ["mail"],
  "baseConfig": "AnalyzerName",
  "command": "analyzers/AnalyzerName/analyzer.py"
}
```

## Testing

Before deploying an analyzer:
1. Test with valid input data
2. Test with missing configuration
3. Test with invalid/malformed data
4. Verify TLP/PAP restrictions work correctly

## Deployment

### Local Deployment
1. Copy analyzer directory to Cortex analyzers path
2. Install requirements: `pip install -r requirements.txt`
3. Configure analyzer settings in Cortex UI

### Docker Deployment
Each analyzer can be containerized for easier deployment. See individual analyzer documentation.

## Contributing

When contributing new analyzers or responders:
1. Follow the established directory structure
2. Include comprehensive documentation
3. Add unit tests where applicable
4. Ensure code follows Python best practices (PEP 8)
5. Document all configuration parameters

## License

AGPL-V3

## Support

For issues or questions:
- GitHub Issues: https://github.com/leonfortej/thehive/issues
- TheHive Documentation: https://docs.strangebee.com/

## Authors

- Development Team
- Powered by StrangeBee TheHive & Cortex

---
**Last Updated**: 2025-10-30
