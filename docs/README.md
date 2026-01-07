# digitalSTROM Virtual Device Connector (vDC) API Documentation

Welcome to the comprehensive documentation for the digitalSTROM vDC API. This documentation has been restructured to make it easier to understand and implement vDC integrations.

## What is this Documentation?

This is a complete rewrite of the digitalSTROM vDC API documentation, designed to be:
- **Clear and accessible** - Easier to understand for developers new to digitalSTROM
- **Well-structured** - Organized by topic and use case
- **Comprehensive** - Covers all aspects of the vDC API
- **Practical** - Includes examples and real-world scenarios

## Documentation Structure

The documentation is organized in a logical learning progression:

1. **[Introduction](01-introduction.md)** - Overview of digitalSTROM and the vDC API
2. **[Quick Start Guide](02-quickstart.md)** - Get up and running quickly with working examples
3. **[Core Concepts](03-core-concepts.md)** - Understanding digitalSTROM basics (zones, groups, scenes)
4. **[vDC Overview](04-vdc-overview.md)** - Virtual Device Connectors explained in detail
5. **[Session Management](05-session-management.md)** - Managing vDC connections and lifecycle
6. **[Protocol Buffers Reference](06-protobuf-reference.md)** - Message format specification
7. **[Properties System](07-properties.md)** - Named properties and how to use them
8. **[Error Handling](08-error-handling.md)** - Error codes and recovery strategies
9. **[Glossary](09-glossary.md)** - Complete terminology reference
10. **[Troubleshooting](10-troubleshooting.md)** - Common issues and debugging guide

## About digitalSTROM

digitalSTROM is a building automation system that enables intelligent control of electrical devices. The vDC API allows IP-based devices to integrate with the digitalSTROM ecosystem, appearing and behaving like native digitalSTROM devices.

## Version Information

This documentation is based on:
- vDC API v3
- API version 2c and later
- Protocol Buffers v2 syntax

## Quick Navigation

**New to digitalSTROM?** Start with [Introduction](01-introduction.md)

**Ready to implement?** Go to [Quick Start Guide](02-quickstart.md)

**Need API details?** See [Protocol Buffers Reference](06-protobuf-reference.md) and [Properties System](07-properties.md)

**Looking for specific terms?** Check the [Glossary](09-glossary.md)

**Having issues?** See [Troubleshooting](10-troubleshooting.md)

## Important Notes

⚠️ **Note on Missing Information**: This documentation consolidates information from multiple source documents. Where information is incomplete, uncertain, or missing, it is clearly marked with:

- 🔍 **UNCLEAR**: Information is ambiguous or contradictory in source documents
- ⚠️ **INCOMPLETE**: Information is partially documented
- ❓ **MISSING**: Information is not available in source documents
- 💡 **ASSUMPTION**: Logical inference based on available information (marked as such)

If you encounter any of these markers and have additional information, please contribute to improve this documentation.

## Contributing

Improvements to this documentation are welcome. Please ensure that:
- Changes maintain clarity and accessibility
- Technical accuracy is preserved
- Examples are tested and working
- Uncertain information is clearly marked

## License

This documentation is based on digitalSTROM AG specifications. Please refer to the original documents for licensing information.

---

**Last Updated**: 2026-01-07  
**Source Documents**: 
- ds-basics.pdf
- vDC-overview.pdf
- vDC-API.pdf
- vDC-API-properties_JULY 2022.pdf
- genericVDC.proto
