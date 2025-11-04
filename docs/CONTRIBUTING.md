# Contributing to TheHive Cortex Analyzers & Responders

Thank you for your interest in contributing to our Cortex analyzers and responders framework!

## How to Contribute

### Reporting Issues

1. Check if the issue already exists in [GitHub Issues](https://github.com/leonfortej/thehive/issues)
2. Create a new issue with:
   - Clear, descriptive title
   - Detailed description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, Cortex version)
   - Relevant log output

### Suggesting Enhancements

1. Open an issue with the "enhancement" label
2. Provide:
   - Clear description of the enhancement
   - Use case and benefits
   - Proposed implementation (if applicable)

### Contributing Code

#### Before You Start

1. Check [open issues](https://github.com/leonfortej/thehive/issues) to avoid duplicate work
2. For major changes, open an issue first to discuss
3. Fork the repository
4. Create a feature branch from `main`

#### Development Process

1. **Set up your environment**
   ```bash
   git clone https://github.com/yourusername/thehive.git
   cd thehive
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the existing code style
   - Add docstrings to all functions and classes
   - Update documentation as needed
   - Add tests if applicable

4. **Test your changes**
   ```bash
   # Test your analyzer
   cat test_input.json | python your_analyzer.py

   # Validate JSON configuration
   python -m json.tool YourAnalyzer.json
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: Add YourFeature analyzer"
   ```

   Use conventional commit messages:
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation changes
   - `refactor:` - Code refactoring
   - `test:` - Adding tests
   - `chore:` - Maintenance tasks

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your feature branch
   - Provide clear description of changes
   - Reference any related issues

#### Code Style Guidelines

**Python**
- Follow PEP 8 style guide
- Use meaningful variable and function names
- Maximum line length: 120 characters
- Use type hints where appropriate
- Add docstrings in Google style format

**Example:**
```python
def process_data(email: str, api_key: str) -> Dict[str, Any]:
    """
    Process user data from API.

    Args:
        email (str): User email address
        api_key (str): API authentication key

    Returns:
        Dict[str, Any]: Processed data dictionary

    Raises:
        ValueError: If email format is invalid
    """
    pass
```

**Documentation**
- Use Markdown format
- Keep line length reasonable (80-100 characters)
- Use clear, concise language
- Include code examples where helpful
- Update relevant documentation when changing code

#### Pull Request Checklist

Before submitting, ensure:

- [ ] Code follows style guidelines
- [ ] All functions have docstrings
- [ ] Tests pass (if applicable)
- [ ] Documentation is updated
- [ ] Commit messages are clear and descriptive
- [ ] No sensitive data (API keys, passwords) in code
- [ ] requirements.txt includes all dependencies
- [ ] Service configuration JSON is valid
- [ ] README.md is included for new analyzers

#### Adding a New Analyzer

When contributing a new analyzer:

1. **Create analyzer directory**
   ```
   analyzers/YourAnalyzer/
   ├── youranalyzer.py
   ├── YourAnalyzer.json
   ├── requirements.txt
   ├── Dockerfile
   ├── README.md
   └── test_input.json
   ```

2. **Required files:**
   - `youranalyzer.py` - Main analyzer code
   - `YourAnalyzer.json` - Service configuration
   - `requirements.txt` - Python dependencies
   - `README.md` - Comprehensive documentation
   - `Dockerfile` - Docker build instructions (optional but recommended)
   - `test_input.json` - Sample test input (for testing)

3. **Documentation requirements:**
   - Overview and purpose
   - Input data types
   - Configuration parameters
   - Output format and taxonomies
   - Installation instructions
   - Usage examples
   - Troubleshooting guide

4. **Test requirements:**
   - Test with valid input
   - Test with missing configuration
   - Test with invalid data
   - Test TLP/PAP restrictions

#### Adding a New Responder

Similar to analyzers, but extend `BaseResponder` and include operation definitions.

### Code Review Process

1. Maintainers will review your pull request
2. Address any feedback or requested changes
3. Once approved, your PR will be merged
4. Your contribution will be credited in release notes

## Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Give credit to others' work
- Follow ethical security practices

### Communication

- **GitHub Issues**: Bug reports, feature requests
- **Pull Requests**: Code contributions
- **Discussions**: General questions and ideas

## Security

### Reporting Security Issues

**DO NOT** open public issues for security vulnerabilities.

Instead:
1. Email security concerns to the maintainers
2. Include detailed description and reproduction steps
3. Allow time for patch development before disclosure

### Security Best Practices

When contributing:
- Never commit API keys, passwords, or credentials
- Validate and sanitize all input data
- Use HTTPS for external API calls
- Follow TLP/PAP restrictions
- Document security considerations

## Testing

### Manual Testing

```bash
# Create test input
cat > test_input.json << EOF
{
  "data": "test-data",
  "dataType": "mail",
  "tlp": 2,
  "pap": 2,
  "config": {
    "param1": "value1"
  }
}
EOF

# Run analyzer
python youranalyzer.py < test_input.json
```

### Automated Testing (Future)

We plan to add:
- Unit tests with pytest
- Integration tests
- CI/CD with GitHub Actions

## Documentation

### Documentation Standards

- Write for users who may not be familiar with the analyzer
- Include practical examples
- Explain configuration parameters clearly
- Document error messages and solutions
- Keep documentation up-to-date with code changes

### Documentation Structure

For each analyzer/responder:
1. **Overview** - What it does and why
2. **Requirements** - Prerequisites and dependencies
3. **Installation** - Step-by-step setup
4. **Configuration** - All parameters explained
5. **Usage** - Examples and workflows
6. **Output** - Expected results format
7. **Troubleshooting** - Common issues and solutions
8. **API/Integration** - External service requirements

## Getting Help

Need help contributing?

- Review [Development Guide](docs/DEVELOPMENT_GUIDE.md)
- Check [existing analyzers](analyzers/) for examples
- Ask questions in GitHub Discussions
- Review [Cortex documentation](https://thehive-project.github.io/Cortex-Analyzers/)

## Recognition

Contributors will be:
- Listed in the AUTHORS file
- Credited in release notes
- Acknowledged in documentation

Thank you for contributing to TheHive Cortex Analyzers & Responders!

---
**Last Updated**: 2025-10-30
