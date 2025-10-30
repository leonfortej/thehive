# Common Utilities Module

This module provides base classes and utilities for building Cortex analyzers and responders.

## Components

### BaseAnalyzer (`base_analyzer.py`)

Base class for all Cortex analyzers. Provides:

- **Input/Output Handling**: Automatic JSON processing via cortexutils
- **TLP/PAP Validation**: Built-in methods to validate Traffic Light Protocol and Permissible Actions Protocol levels
- **Configuration Management**: Easy parameter access and validation
- **Taxonomy Generation**: Helper methods for creating TheHive taxonomies
- **Error Handling**: Standardized error reporting
- **Logging**: Built-in logging configuration

#### Usage Example

```python
from common.base_analyzer import BaseAnalyzer

class MyAnalyzer(BaseAnalyzer):
    def __init__(self):
        super(MyAnalyzer, self).__init__()

    def run(self):
        # Validate TLP
        self.validate_tlp(max_tlp=2)

        # Get parameters
        api_key = self.get_param('config.api_key', None, 'API key is required')
        data = self.get_data()

        # Perform analysis
        results = self.do_analysis(data)

        # Report results
        self.report({
            'success': True,
            'data': results
        })
```

### BaseResponder (`base_responder.py`)

Base class for all Cortex responders. Provides:

- **Input/Output Handling**: Automatic JSON processing
- **Configuration Management**: Parameter access and validation
- **Operation Reporting**: Methods for reporting responder operations
- **Error Handling**: Standardized error reporting
- **Logging**: Built-in logging configuration

#### Usage Example

```python
from common.base_responder import BaseResponder

class MyResponder(BaseResponder):
    def __init__(self):
        super(MyResponder, self).__init__()

    def run(self):
        # Get parameters
        observable = self.get_param('data', None, 'Observable data required')

        # Perform action
        result = self.do_action(observable)

        # Report results
        self.report({
            'success': True,
            'message': 'Action completed successfully'
        })
```

### APIClient (`utils.py`)

HTTP client for making REST API calls. Features:

- **GET/POST Methods**: Standardized HTTP methods
- **Error Handling**: Automatic retry and error management
- **Timeout Management**: Configurable request timeouts
- **SSL Verification**: Optional SSL certificate verification
- **Header Management**: Default and custom header support
- **Response Parsing**: Automatic JSON parsing

#### Usage Example

```python
from common.utils import APIClient

# Initialize client
client = APIClient(
    base_url='https://api.example.com',
    timeout=30,
    verify_ssl=True,
    headers={'Authorization': 'Bearer token123'}
)

# Make GET request
response = client.get('/users', params={'email': 'user@example.com'})

# Make POST request
response = client.post('/data', data={'key': 'value'})
```

### DataValidator (`utils.py`)

Input validation utilities for common data types. Provides:

- **Email Validation**: RFC-compliant email format checking
- **IP Address Validation**: IPv4 address validation
- **Domain Validation**: Domain name format checking
- **URL Validation**: HTTP/HTTPS URL validation
- **Hash Validation**: MD5, SHA1, SHA256 hash format checking
- **String Sanitization**: Remove potentially harmful characters

#### Usage Example

```python
from common.utils import DataValidator

validator = DataValidator()

# Validate email
if validator.is_valid_email('user@example.com'):
    print('Valid email')

# Validate IP address
if validator.is_valid_ip('192.168.1.1'):
    print('Valid IP')

# Validate hash
if validator.is_valid_hash('d41d8cd98f00b204e9800998ecf8427e', 'md5'):
    print('Valid MD5 hash')

# Sanitize input
clean_text = validator.sanitize_string(user_input)
```

## Installation

The common module requires:

- Python 3.8+
- cortexutils
- requests

Install dependencies:
```bash
pip install cortexutils requests
```

## Development Guidelines

### Creating a New Analyzer

1. Import BaseAnalyzer:
   ```python
   from common.base_analyzer import BaseAnalyzer
   ```

2. Extend the class:
   ```python
   class MyAnalyzer(BaseAnalyzer):
       def __init__(self):
           super(MyAnalyzer, self).__init__()
   ```

3. Implement the `run()` method:
   ```python
   def run(self):
       # Your analyzer logic here
       pass
   ```

4. Override `summary()` for custom taxonomies:
   ```python
   def summary(self, raw):
       taxonomies = []
       # Build your taxonomies
       return {'taxonomies': taxonomies}
   ```

5. Override `artifacts()` to extract observables:
   ```python
   def artifacts(self, raw):
       artifacts = []
       # Extract artifacts from results
       return artifacts
   ```

### Best Practices

1. **Always validate input**: Use `check_required_params()` and DataValidator
2. **Handle errors gracefully**: Use try/except blocks and call `self.error()`
3. **Log important events**: Use `self.logger` for debugging
4. **Validate TLP/PAP**: Call `validate_tlp()` and `validate_pap()` when needed
5. **Build meaningful taxonomies**: Use descriptive namespaces and predicates
6. **Document your code**: Include docstrings and comments

## Logging

All base classes include logging configured to stderr. Log levels:

- **INFO**: Normal operation events
- **WARNING**: Unexpected but handled situations
- **ERROR**: Error conditions that may affect functionality
- **DEBUG**: Detailed diagnostic information

Access the logger in your analyzer/responder:
```python
self.logger.info('Processing data...')
self.logger.warning('Unusual condition detected')
self.logger.error('Failed to connect to API')
```

## Error Handling

Use the built-in error method to report failures:

```python
# Report error and exit
self.error('API key not configured')

# With exception handling
try:
    result = risky_operation()
except Exception as e:
    self.error(f'Operation failed: {str(e)}')
```

## Configuration Parameters

Access configuration via `get_param()`:

```python
# Get required parameter
api_key = self.get_param('config.api_key', None, 'API key required')

# Get optional parameter with default
timeout = self.get_param('config.timeout', 30)

# Check multiple required parameters
self.check_required_params(['api_key', 'api_url'])
```

---
**Last Updated**: 2025-10-30
