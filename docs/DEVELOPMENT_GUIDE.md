# Development Guide

This guide provides detailed information for developers working on Cortex analyzers and responders for TheHive.

## Table of Contents

1. [Environment Setup](#environment-setup)
2. [Project Structure](#project-structure)
3. [Creating a New Analyzer](#creating-a-new-analyzer)
4. [Creating a New Responder](#creating-a-new-responder)
5. [Testing](#testing)
6. [Best Practices](#best-practices)
7. [Deployment](#deployment)

## Environment Setup

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Git
- Text editor or IDE (VS Code, PyCharm, etc.)

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/leonfortej/thehive.git
cd thehive

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Project Structure

```
thehive/
├── analyzers/              # Analyzer implementations
│   └── UserLogonHistory/   # Example analyzer
│       ├── userlogonhistory.py
│       ├── UserLogonHistory.json
│       ├── requirements.txt
│       ├── Dockerfile
│       └── README.md
├── responders/             # Responder implementations
├── common/                 # Shared utilities
│   ├── __init__.py
│   ├── base_analyzer.py   # Base analyzer class
│   ├── base_responder.py  # Base responder class
│   ├── utils.py           # Utility functions
│   └── README.md
├── templates/              # Report templates
├── docs/                   # Documentation
├── requirements.txt        # Project dependencies
└── README.md              # Main readme
```

## Creating a New Analyzer

### Step 1: Create Directory Structure

```bash
mkdir -p analyzers/MyAnalyzer
cd analyzers/MyAnalyzer
```

### Step 2: Create the Analyzer Python File

Create `myanalyzer.py`:

```python
#!/usr/bin/env python3
import sys
import os

# Add common module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from common.base_analyzer import BaseAnalyzer
from common.utils import APIClient, DataValidator


class MyAnalyzer(BaseAnalyzer):
    """Your analyzer description."""

    def __init__(self):
        super(MyAnalyzer, self).__init__()
        # Initialize your analyzer
        self.validate_tlp(max_tlp=2)
        self.api_key = self.get_param('config.api_key', None, 'API key required')
        self.data = self.get_data()

    def run(self):
        """Main analyzer logic."""
        try:
            # Your analysis logic here
            result = self.analyze(self.data)

            # Report success
            self.report({
                'success': True,
                'result': result
            })

        except Exception as e:
            self.logger.error(f'Analysis failed: {str(e)}')
            self.error(f'Analysis failed: {str(e)}')

    def summary(self, raw):
        """Generate taxonomies."""
        taxonomies = []

        if raw.get('success'):
            taxonomies.append(
                self.build_taxonomy(
                    namespace='MyAnalyzer',
                    predicate='Status',
                    value='Complete',
                    level='info'
                )
            )

        return {'taxonomies': taxonomies}


if __name__ == '__main__':
    MyAnalyzer().run()
```

### Step 3: Create Service Configuration

Create `MyAnalyzer.json`:

```json
{
  "name": "MyAnalyzer",
  "version": "1.0.0",
  "author": "Your Name",
  "url": "https://github.com/leonfortej/thehive",
  "license": "AGPL-V3",
  "description": "Description of what your analyzer does",
  "dataTypeList": ["ip", "domain", "mail"],
  "baseConfig": "MyAnalyzer",
  "command": "analyzers/MyAnalyzer/myanalyzer.py",
  "configurationItems": [
    {
      "name": "api_key",
      "description": "API key for the service",
      "type": "string",
      "multi": false,
      "required": true,
      "defaultValue": ""
    }
  ],
  "config": {
    "check_tlp": true,
    "max_tlp": 2,
    "check_pap": true,
    "max_pap": 2
  }
}
```

### Step 4: Create Requirements File

Create `requirements.txt`:

```
cortexutils>=2.2.1
requests>=2.31.0
# Add other dependencies
```

### Step 5: Create Documentation

Create `README.md` with:
- Overview and purpose
- Input data types
- Configuration parameters
- Output format
- Installation instructions
- Usage examples
- Troubleshooting

### Step 6: Create Dockerfile (Optional)

Create `Dockerfile` for containerized deployment.

## Creating a New Responder

Similar to analyzers but extend `BaseResponder` instead:

```python
from common.base_responder import BaseResponder

class MyResponder(BaseResponder):
    def __init__(self):
        super(MyResponder, self).__init__()

    def run(self):
        # Responder logic
        pass

    def operations(self, raw):
        return []
```

## Testing

### Manual Testing

Create a test input file `test_input.json`:

```json
{
  "data": "test@example.com",
  "dataType": "mail",
  "tlp": 2,
  "pap": 2,
  "config": {
    "api_key": "test-key"
  }
}
```

Run the analyzer:

```bash
cat test_input.json | python myanalyzer.py
```

### Test Cases

Test these scenarios:
1. **Normal execution** - Valid input and configuration
2. **Missing configuration** - Required parameters missing
3. **Invalid data type** - Wrong data type provided
4. **TLP/PAP restrictions** - Exceeding maximum levels
5. **API failures** - Network errors, timeouts, invalid responses

### Automated Testing

Create unit tests in `tests/` directory:

```python
import unittest
from analyzers.MyAnalyzer.myanalyzer import MyAnalyzer

class TestMyAnalyzer(unittest.TestCase):
    def test_valid_input(self):
        # Test valid input
        pass

    def test_invalid_input(self):
        # Test invalid input
        pass
```

## Best Practices

### Code Quality

1. **Follow PEP 8** - Python style guide
2. **Use type hints** - Improve code clarity
3. **Write docstrings** - Document all classes and methods
4. **Error handling** - Use try/except blocks
5. **Logging** - Log important events

### Security

1. **Validate input** - Use DataValidator class
2. **Sanitize data** - Clean user input
3. **Secure credentials** - Never hardcode API keys
4. **TLP/PAP compliance** - Enforce data sharing restrictions
5. **SSL verification** - Use HTTPS with verification

### Performance

1. **Timeouts** - Set reasonable request timeouts
2. **Rate limiting** - Respect API rate limits
3. **Caching** - Cache responses when appropriate
4. **Async operations** - Use async for I/O operations when needed

### Documentation

1. **README** - Comprehensive analyzer documentation
2. **Code comments** - Explain complex logic
3. **Configuration** - Document all parameters
4. **Examples** - Provide usage examples
5. **Troubleshooting** - Common issues and solutions

## Deployment

### Local Deployment

1. Copy analyzer to Cortex analyzers directory
2. Install dependencies
3. Configure in Cortex UI
4. Test with sample data

### Docker Deployment

Build and run using Docker:

```bash
# Build image
docker build -t myanalyzer:1.0 .

# Test locally
docker run -i myanalyzer:1.0 < test_input.json
```

### Production Considerations

1. **Monitoring** - Set up log monitoring
2. **Error alerting** - Alert on failures
3. **Performance tracking** - Monitor execution times
4. **Resource limits** - Set memory/CPU limits
5. **High availability** - Deploy multiple instances

## Git Workflow

### Branching Strategy

- `main` - Production-ready code
- `develop` - Integration branch
- `feature/*` - Feature branches
- `bugfix/*` - Bug fix branches

### Commit Messages

Follow conventional commits:
```
feat: Add new analyzer for user logon history
fix: Correct email validation in UserLogonHistory
docs: Update installation instructions
refactor: Improve error handling in base analyzer
test: Add unit tests for APIClient
```

### Pull Request Process

1. Create feature branch
2. Implement changes
3. Test thoroughly
4. Update documentation
5. Create pull request
6. Address review comments
7. Merge when approved

## Code Review Checklist

- [ ] Code follows PEP 8 style guide
- [ ] All methods have docstrings
- [ ] Error handling is comprehensive
- [ ] Input validation is implemented
- [ ] TLP/PAP restrictions are enforced
- [ ] Logging is appropriate
- [ ] Tests are included
- [ ] Documentation is updated
- [ ] No hardcoded credentials
- [ ] Dockerfile works (if applicable)

## Resources

### Cortex Documentation
- [Cortex Analyzers Documentation](https://thehive-project.github.io/Cortex-Analyzers/)
- [Creating Analyzers Guide](https://thehive-project.github.io/Cortex-Analyzers/dev_guides/how-to-create-an-analyzer/)
- [Official Analyzer Repository](https://github.com/TheHive-Project/Cortex-Analyzers)

### TheHive Documentation
- [TheHive Documentation](https://docs.strangebee.com/)
- [Cortex Integration](https://docs.strangebee.com/cortex/)

### Python Resources
- [PEP 8 Style Guide](https://peps.python.org/pep-0008/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [Cortexutils Library](https://pypi.org/project/cortexutils/)

## Getting Help

- GitHub Issues: https://github.com/leonfortej/thehive/issues
- TheHive Community: https://community.thehive-project.org/
- Cortex Documentation: https://thehive-project.github.io/Cortex-Analyzers/

---
**Last Updated**: 2025-10-30
