# Introduction to digitalSTROM vDC API

## What is digitalSTROM?

digitalSTROM is a building automation system that uses existing electrical wiring to create an intelligent network of devices. It enables centralized control of lights, blinds, heating, and other electrical devices throughout a building.

### Key Features

- **Distributed Intelligence**: Control logic is distributed across devices rather than centralized
- **Powerline Communication**: Uses existing electrical wiring (dS485 protocol)
- **Scene-Based Control**: Pre-configured states that control multiple devices simultaneously
- **Application Groups**: Devices organized by function (light, shade, heating, etc.)
- **Zone-Based Organization**: Devices grouped by physical location (rooms, areas)

## What is a Virtual Device Connector (vDC)?

A **Virtual Device Connector (vDC)** is a software component that enables IP-based devices to integrate into the digitalSTROM system. Through vDC, external devices appear and behave like native digitalSTROM devices.

### Why Use vDC?

The vDC API allows you to:

1. **Integrate IP Devices**: Connect WiFi, Ethernet, or other IP-based devices to digitalSTROM
2. **Bridge Other Protocols**: Create gateways to other automation systems (EnOcean, DALI, Zigbee, etc.)
3. **Extend Functionality**: Add custom devices or functionality to digitalSTROM
4. **Maintain Compatibility**: Integrated devices work seamlessly with existing digitalSTROM features

## System Components

### Core Components

```
┌─────────────────────────────────────────────────────┐
│                digitalSTROM Server (dSS)            │
│  - Configuration & Management                       │
│  - User Interface                                   │
│  - High-level automation                            │
└──────────────────────┬──────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
┌───────▼───────┐            ┌────────▼────────┐
│ dSM (Meters)  │            │ vdSM (Virtual)  │
│ - Power line  │            │ - IP devices    │
│ - dS485       │            │ - vDC API       │
└───────┬───────┘            └────────┬────────┘
        │                             │
  ┌─────┴─────┐              ┌────────┴────────┐
  │           │              │                 │
┌─▼─┐      ┌─▼─┐         ┌─▼──┐           ┌──▼──┐
│dSD│      │dSD│         │vDC │           │vDC  │
└───┘      └───┘         └────┘           └─────┘
Physical                 Virtual Devices
Devices
```

### Component Descriptions

| Component | Description |
|-----------|-------------|
| **dSS** | digitalSTROM Server - Central configuration and management |
| **dSM** | digitalSTROM Meter - Powerline communication master |
| **vdSM** | Virtual dSM - Connects to vDC hosts via IP/TCP |
| **dSD** | digitalSTROM Device - Physical terminal block on powerline |
| **vDC** | Virtual Device Connector - Logical entity representing device class |
| **vDC Host** | Physical device running vDC software, offering TCP socket |
| **vdSD** | Virtual dS Device - Single virtual device in the system |

## Device Integration Types

The vDC API supports three main integration patterns:

### Type 1: Server-Side vDC
- vDC runs on the digitalSTROM Server
- Devices communicate with dSS directly
- Best for: Simple IP devices, REST APIs, cloud services

```
┌─────────┐         ┌─────────────────┐
│ Device  │◄───IP──►│ dSS with vDC    │
└─────────┘         └─────────────────┘
```

### Type 2: Device-Side vDC
- vDC runs on the physical device itself
- Device offers vDC API server socket
- Best for: Smart devices with computing power

```
┌─────────────────┐         ┌─────────┐
│ Device with vDC │◄───IP──►│  dSS    │
│  (vDC Host)     │         │ (vdSM)  │
└─────────────────┘         └─────────┘
```

### Type 3: Gateway vDC
- vDC runs on a gateway device
- Gateway bridges to other protocols/devices
- Best for: Multiple devices, non-IP protocols

```
┌──────────────────────────┐         ┌─────────┐
│  Gateway (vDC Host)      │◄───IP──►│  dSS    │
│  ┌────┐  ┌────┐  ┌────┐ │         │ (vdSM)  │
│  │Dev1│  │Dev2│  │Dev3│ │         └─────────┘
│  └────┘  └────┘  └────┘ │
│  (EnOcean/DALI/Zigbee)   │
└──────────────────────────┘
```

## Communication Overview

### Protocol Stack

The vDC API uses the following communication stack:

1. **Transport**: TCP socket connection
2. **Framing**: 2-byte length header (network byte order) + message data
3. **Encoding**: Google Protocol Buffers (protobuf v2)
4. **API**: vDC message types and properties

### Message Flow

```
vdSM (Client)                    vDC Host (Server)
     │                                  │
     ├────── TCP Connect ──────────────►│
     │                                  │
     ├────── RequestHello ─────────────►│
     │◄───── ResponseHello ─────────────┤
     │                                  │
     ├────── RequestGetProperty ───────►│
     │◄───── ResponseGetProperty ───────┤
     │                                  │
     │◄───── SendAnnounceDevice ────────┤
     │                                  │
     ├────── NotificationCallScene ────►│
     │                                  │
     │◄───── SendPushNotification ──────┤
     │                                  │
```

## Key Concepts

### Sessions
A **vDC session** is the logical connection between a vdSM and a vDC host. The session lifetime is tied to the TCP connection - if the connection breaks, a new session must be established.

### Unique Identifiers (dSUID)
Every entity in digitalSTROM has a **dSUID** (digitalSTROM Unique Identifier):
- vDC hosts have dSUIDs
- Virtual devices (vdSD) have dSUIDs
- Logical vDCs have dSUIDs

The dSUID is a 17-byte identifier represented as a 34-character hex string.

### Properties
The vDC API uses a **named property system** for configuration and state:
- Hierarchical structure (tree-like)
- Read/write access control
- Type-safe values (bool, int, double, string, bytes)
- Properties describe device capabilities, configuration, and state

### Scenes
**Scenes** are pre-configured states that affect multiple devices:
- Scene numbers represent specific states (e.g., "Off", "On", "Scene 1-4")
- Devices store scene values locally
- Scenes can be group-specific or zone-wide
- Special scenes exist for system states (Panic, Fire, etc.)

## Development Approach

### Choosing Your Path

**Option 1: Use libdsvdc (C Library)**
- Lightweight C library
- Suitable for embedded systems
- Best for device types 1 & 2
- Lower-level, more control

**Option 2: Use vdcd (C++ Framework)**
- Full-featured framework
- Built-in device class support
- Best for gateway devices (type 3)
- Higher-level abstractions

**Option 3: Implement from Scratch**
- Use this documentation + Protocol Buffers
- Any programming language with protobuf support
- Full flexibility
- More development effort

### Prerequisites

To work with vDC API, you should understand:

- **TCP/IP networking** - Socket programming basics
- **Protocol Buffers** - Google's serialization format
- **digitalSTROM concepts** - Scenes, groups, zones (covered in this documentation)
- **Your device's API** - How to control your specific device

## What's Next?

- **[Quick Start Guide](02-quickstart.md)** - Get started with a simple example
- **[Core Concepts](03-core-concepts.md)** - Deep dive into digitalSTROM fundamentals
- **[vDC Overview](05-vdc-overview.md)** - Detailed vDC architecture

---

**Need Help?** Check the [Glossary](15-glossary.md) for term definitions or [Troubleshooting](17-troubleshooting.md) for common issues.
