# DS-pyVDC-API

## digitalSTROM Virtual Device Connector (vDC) API Documentation & Python Implementation

This repository contains:
- **Complete Python implementation** of the digitalSTROM vDC API
- **Comprehensive documentation** for the vDC protocol

### 🐍 [Python Implementation](README_IMPLEMENTATION.md) | 📚 [Read the Documentation](docs/README.md)

## Python Implementation

This repository now includes a complete Python implementation of the vDC API!

**Key Features:**
- ✅ Full vDC API v3 support with Protocol Buffers
- ✅ Easy-to-use `VdcHost` and `VdcDevice` classes
- ✅ Automatic session management and device announcements
- ✅ Extensible device classes for custom implementations
- ✅ Complete examples and documentation

**Quick Start:**
```python
from ds_vdc_api import VdcHost, VdcDevice

host = VdcHost(dsuid="...", vdc_dsuid="...", port=8444)
device = VdcDevice(dsuid="...", name="My Light", device_class="Light")
host.add_device(device)
host.start()
```

👉 **[Full Implementation Guide](README_IMPLEMENTATION.md)**

## vDC API Documentation

The `/docs` directory contains comprehensive vDC protocol documentation rewritten to be:
- **Easier to understand** - Clear explanations for developers new to digitalSTROM
- **Better organized** - Structured by topic and use case
- **More complete** - Covers all aspects of the vDC API
- **More practical** - Includes examples and real-world scenarios

### Quick Start

- **New to digitalSTROM?** → [Introduction](docs/01-introduction.md)
- **Ready to implement?** → [Quick Start Guide](docs/02-quickstart.md)
- **Need API reference?** → [Protocol Buffers](docs/06-protobuf-reference.md) | [Properties](docs/07-properties.md)
- **Looking for terms?** → [Glossary](docs/09-glossary.md)
- **Having issues?** → [Troubleshooting](docs/10-troubleshooting.md)

### What's Inside

The `/docs` directory contains 10 documents in a logical learning progression:

1. **[Introduction](docs/01-introduction.md)** - Overview of digitalSTROM and vDC
2. **[Quick Start Guide](docs/02-quickstart.md)** - Build your first vDC integration
3. **[Core Concepts](docs/03-core-concepts.md)** - Fundamental concepts (zones, groups, scenes)
4. **[vDC Overview](docs/04-vdc-overview.md)** - Virtual Device Connectors explained
5. **[Session Management](docs/05-session-management.md)** - Connection lifecycle
6. **[Protocol Buffers Reference](docs/06-protobuf-reference.md)** - Message formats
7. **[Properties System](docs/07-properties.md)** - Named properties reference
8. **[Error Handling](docs/08-error-handling.md)** - Error codes and recovery
9. **[Glossary](docs/09-glossary.md)** - Complete terminology reference
10. **[Troubleshooting](docs/10-troubleshooting.md)** - Debugging guide

### Original Documentation

The original PDF documentation is preserved in the `/original_docs` directory:
- `ds-basics.pdf` - digitalSTROM system basics
- `vDC-overview.pdf` - vDC system overview
- `vDC-API.pdf` - vDC API specification
- `vDC-API-properties_JULY 2022.pdf` - Properties reference
- `genericVDC.proto` - Protocol Buffer definitions

### About

This documentation rewrite aims to make the digitalSTROM vDC API more accessible to developers. It consolidates information from multiple source documents into a cohesive, easy-to-navigate structure.

### Contributing

Improvements and corrections are welcome! Please ensure:
- Technical accuracy is maintained
- Clarity and accessibility are preserved
- Uncertain information is clearly marked

### License

Based on digitalSTROM AG specifications. See original documents for licensing information.