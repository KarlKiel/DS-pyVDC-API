# Contributing to DS-pyVDC-API

First off, thank you for considering contributing to DS-pyVDC-API! It's people like you that make DS-pyVDC-API such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the issue list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* Use a clear and descriptive title
* Describe the exact steps which reproduce the problem
* Provide specific examples to demonstrate the steps
* Describe the behavior you observed after following the steps
* Explain which behavior you expected to see instead and why
* Include Python version, OS, and relevant package versions

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* Use a clear and descriptive title
* Provide a step-by-step description of the suggested enhancement
* Provide specific examples to demonstrate the steps
* Describe the current behavior and explain which behavior you expected to see instead
* Explain why this enhancement would be useful

### Pull Requests

* Fill in the required template
* Do not include issue numbers in the PR title
* Follow the Python style guide (PEP 8)
* Include thoughtfully-worded, well-structured tests
* Document new code
* End all files with a newline

## Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/DS-pyVDC-API.git
   cd DS-pyVDC-API
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

5. Create a branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Style Guidelines

### Python Style Guide

* Follow PEP 8
* Use Black for code formatting (line length: 88)
* Use type hints where appropriate
* Write docstrings for all public modules, functions, classes, and methods
* Keep functions focused and small

### Git Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line

### Testing

* Write tests for all new features
* Ensure all tests pass before submitting PR
* Aim for high code coverage
* Use descriptive test names

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=ds_pyvdc_api

# Run linting
flake8 src/ tests/

# Run type checking
mypy src/

# Format code
black src/ tests/
```

## Additional Notes

### Issue and Pull Request Labels

* `bug` - Something isn't working
* `enhancement` - New feature or request
* `documentation` - Improvements or additions to documentation
* `good first issue` - Good for newcomers
* `help wanted` - Extra attention is needed

Thank you for contributing! 🎉
