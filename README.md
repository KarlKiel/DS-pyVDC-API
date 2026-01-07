# DS-pyVDC-API

A Python API library for VDC (Virtual Data Center) operations.

## Features

- Simple and intuitive API interface
- Type-safe configuration management
- Comprehensive error handling
- Extensible architecture
- Well-documented codebase

## Installation

### From PyPI (when published)

```bash
pip install ds-pyvdc-api
```

### From Source

```bash
git clone https://github.com/KarlKiel/DS-pyVDC-API.git
cd DS-pyVDC-API
pip install -e .
```

### Development Installation

```bash
pip install -e ".[dev]"
```

## Quick Start

```python
from ds_pyvdc_api import VDCClient

# Initialize the client
client = VDCClient(
    base_url="https://api.example.com",
    api_key="your_api_key_here"
)

# Connect to the API
client.connect()

# Perform operations
# ...

# Disconnect when done
client.disconnect()
```

## Project Structure

```
DS-pyVDC-API/
├── src/
│   └── ds_pyvdc_api/       # Main package
│       ├── __init__.py     # Package initialization
│       ├── api.py          # Main API client
│       ├── config.py       # Configuration management
│       ├── exceptions.py   # Custom exceptions
│       └── utils.py        # Utility functions
├── tests/                  # Test suite
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_config.py
│   └── test_utils.py
├── examples/               # Usage examples
│   ├── basic_usage.py
│   └── config_example.py
├── docs/                   # Documentation
├── .gitignore             # Git ignore rules
├── .flake8                # Flake8 configuration
├── .editorconfig          # Editor configuration
├── pyproject.toml         # Modern Python package configuration
├── setup.py               # Setup script
├── requirements.txt       # Production dependencies
├── requirements-dev.txt   # Development dependencies
├── MANIFEST.in            # Package manifest
├── LICENSE                # GPL-3.0 License
└── README.md              # This file
```

## Development

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

### Running Examples

```bash
python examples/basic_usage.py
python examples/config_example.py
```

## Configuration

The library can be configured using:

1. **Environment Variables**:
   - `VDC_API_URL`: Base URL for the VDC API
   - `VDC_API_KEY`: API key for authentication

2. **Configuration Object**:
   ```python
   from ds_pyvdc_api.config import Config
   
   config = Config()
   config.base_url = "https://api.example.com"
   config.api_key = "your_key"
   config.timeout = 60
   ```

3. **Direct Client Initialization**:
   ```python
   client = VDCClient(base_url="...", api_key="...")
   ```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Authors

- **KarlKiel** - Initial work

## Acknowledgments

- Thanks to all contributors who help improve this project