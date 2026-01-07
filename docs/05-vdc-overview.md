# vDC Overview

This document provides a detailed overview of Virtual Device Connectors (vDC) and how they enable IP-based devices to integrate with digitalSTROM.

## What is a vDC?

A **Virtual Device Connector (vDC)** is a software component that bridges IP-based devices to the digitalSTROM system. It makes external devices appear and behave exactly like native digitalSTROM terminal blocks (dSD).

### vDC Ecosystem Components

```
┌─────────────────────────────────────────┐
│    digitalSTROM Server (dSS)            │
│    - Configuration UI                   │
│    - Automation Engine                  │
│    - Hosts vdSM instances               │
└────────────────┬────────────────────────┘
                 │
                 │ vDC API (TCP/IP)
                 │
        ┌────────┴────────┐
        │                 │
┌───────▼───────┐   ┌────▼──────┐
│ vDC Host 1    │   │vDC Host 2 │
│ - Runs vDC(s) │   │- Gateway  │
│ - TCP Server  │   │- Protocol │
│               │   │  Bridge   │
│  ┌────────┐   │   │           │
│  │ vDC 1  │   │   │ ┌──────┐  │
│  │ vdSD A │   │   │ │vDC 1 │  │
│  │ vdSD B │   │   │ │vdSD X│  │
│  └────────┘   │   │ │vdSD Y│  │
│               │   │ └──────┘  │
│  ┌────────┐   │   │ ┌──────┐  │
│  │ vDC 2  │   │   │ │vDC 2 │  │
│  │ vdSD C │   │   │ │vdSD Z│  │
│  └────────┘   │   │ └──────┘  │
└───────────────┘   └───────────┘
```

### Key Terminology

| Term | Description |
|------|-------------|
| **vDC** | Virtual Device Connector - Logical entity representing a device class with its own dSUID |
| **vDC Host** | Physical or virtual device offering a TCP server socket for vdSM to connect to |
| **vdSM** | Virtual digitalSTROM Meter - Client that connects to vDC hosts (runs on dSS) |
| **vdSD** | Virtual digitalSTROM Device - Individual device represented in the system |
| **vDC Session** | Logical connection between vdSM and vDC host (tied to TCP connection lifetime) |

## vDC Integration Types

digitalSTROM supports three main integration patterns:

### Type 1: Server-Side vDC

**Configuration:**
- vDC runs within the digitalSTROM Server (dSS)
- Both vDC and vdSM run on the same dSS
- Device communicates with dSS via its own protocol/API

**Use Cases:**
- Simple IP devices with REST APIs
- Cloud-connected devices
- Devices without computational resources for running vDC
- Quick integration prototypes

**Pros:**
- Easiest to deploy (no software on device)
- Centralized management
- No additional hardware needed

**Cons:**
- Device must be reachable from dSS
- Limited scalability for many devices
- Dependent on dSS connectivity

**Example:**
```
Cloud Service API ←→ dSS (vDC + vdSM) ←→ dSS Storage
```

### Type 2: Device-Side vDC

**Configuration:**
- vDC runs on the device itself
- Device acts as vDC host with TCP server
- vdSM on dSS connects to device

**Use Cases:**
- Smart devices with embedded processors
- Devices with permanent network connection
- Standalone intelligent devices

**Pros:**
- Device is self-contained
- Can work independently
- Better encapsulation

**Cons:**
- Device must run vDC software
- Requires device development resources
- Device must maintain network connection

**Example:**
```
Smart Thermostat (vDC Host) ←TCP→ dSS (vdSM)
```

### Type 3: Gateway vDC

**Configuration:**
- vDC runs on a gateway device
- Gateway bridges to other protocols/technologies
- Multiple devices connect through gateway

**Use Cases:**
- EnOcean devices (radio protocol)
- DALI lighting systems (bus protocol)
- Zigbee sensor networks
- Proprietary bus systems
- Groups of similar devices

**Pros:**
- Integrates entire device classes
- Protocol bridging
- Centralized gateway management
- Scalable to many devices

**Cons:**
- Requires gateway hardware
- Gateway is single point of failure
- More complex architecture

**Example:**
```
EnOcean Sensors →(radio)→ Gateway (vDC Host) ←TCP→ dSS (vdSM)
DALI Lights -----(bus)--→ Gateway (vDC Host) ←TCP→ dSS (vdSM)
```

## vDC Architecture

### Hierarchical Structure

A vDC host can host multiple logical vDCs, and each vDC can host multiple virtual devices:

```
vDC Host (192.168.1.100:8444)
│
├─ vDC: Lighting Class (dSUID: ABC...)
│  ├─ vdSD: Living Room Lamp (dSUID: 123...)
│  ├─ vdSD: Kitchen Light (dSUID: 456...)
│  └─ vdSD: Bedroom Light (dSUID: 789...)
│
└─ vDC: Sensor Class (dSUID: DEF...)
   ├─ vdSD: Temperature Sensor (dSUID: 234...)
   └─ vdSD: Motion Sensor (dSUID: 567...)
```

### Why Multiple vDCs?

A single vDC host can host multiple logical vDCs when:

- Supporting multiple device classes (lights + sensors)
- Bridging multiple protocols (EnOcean + DALI)
- Organizing devices logically
- Different vendors/manufacturers

**Each vDC:**
- Has its own dSUID
- Represents a device class or category
- Can be managed independently
- Is announced separately to vdSM

## Connection and Discovery

### Avahi/Bonjour Service Discovery

vDC hosts must announce themselves using Avahi (Bonjour on macOS):

**Service Type:** `_ds-vdc._tcp`

**Announcement Example:**
```xml
<?xml version="1.0" standalone='no'?>
<!DOCTYPE service-group SYSTEM "avahi-service.dtd">
<service-group>
  <name replace-wildcards="yes">My Smart Lights on %h</name>
  <service protocol="ipv4">
    <type>_ds-vdc._tcp</type>
    <port>8444</port>
  </service>
</service-group>
```

### Discovery Process

```
1. vDC Host starts and announces via Avahi
2. vdSM (on dSS) scans network for _ds-vdc._tcp services
3. vdSM checks against optional whitelist
4. vdSM connects to vDC host TCP socket
5. Session initialization begins
```

### Whitelisting (Optional)

To prevent unwanted connections in complex installations:

- Whitelists are stored on dSS
- Only whitelisted vDC hosts are connected
- Useful in showrooms, development environments, multi-tenant buildings

🔍 **UNCLEAR**: Exact whitelist format and configuration method not fully documented

## Connection Management

### TCP Socket Connection

**Characteristics:**
- vdSM initiates connection (client)
- vDC host accepts connection (server)
- Standard TCP/IP socket
- Conventional port: 8444 (configurable)
- IPv4 (IPv6 planned for future)

### Session Lifecycle

```
┌─────────┐                          ┌──────────┐
│  vdSM   │                          │vDC Host  │
└────┬────┘                          └────┬─────┘
     │                                    │
     │──────── TCP Connect ──────────────►│
     │                                    │
     │◄────── TCP Accept ─────────────────┤
     │                                    │
     │   SESSION INITIALIZATION           │
     │   (Hello handshake)                │
     │                                    │
     │   SESSION OPERATION                │
     │   (Property access, notifications) │
     │                                    │
     │   SESSION TERMINATION              │
     │   (Bye or disconnect)              │
     │                                    │
     │──────── TCP Close ────────────────►│
     │                                    │
```

**Key Points:**

1. **Session = TCP Connection**: If TCP breaks, session ends
2. **One Session at a Time**: vDC host typically serves one vdSM
3. **Reconnection**: After disconnect, new session must be initialized
4. **State is Stateful**: Session maintains state; must re-announce devices after reconnect

### Exclusive Connection

⚠️ **IMPORTANT**: A vDC host should only be connected to one vdSM at a time:

- Multiple connections can cause conflicts
- vDC host may reject additional connections
- Error `ERR_SERVICE_NOT_AVAILABLE` if already connected

**Exception**: Advanced gateway scenarios may support multiple connections, but this is not standard.

## Device Lifecycle

### 1. Device Announcement

After session is established, vDC must announce its devices:

```
┌─────────┐                          ┌──────────┐
│  vdSM   │                          │vDC Host  │
└────┬────┘                          └────┬─────┘
     │                                    │
     │   (Session established)            │
     │                                    │
     │◄─── VDC_SEND_ANNOUNCE_VDC ─────────┤
     │     (announce vDC itself)          │
     │                                    │
     │◄─── VDC_SEND_ANNOUNCE_DEVICE ──────┤
     │     (announce device 1)            │
     │                                    │
     │◄─── VDC_SEND_ANNOUNCE_DEVICE ──────┤
     │     (announce device 2)            │
     │                                    │
```

### 2. Device Operation

During normal operation:

- vdSM queries device properties
- vdSM sends notifications (scene calls, dimming, etc.)
- vDC pushes state changes to vdSM

### 3. Device Removal

To remove a device from the system:

```
vDC Host sends: VDC_SEND_VANISH (dSUID of device)
```

The device disappears from the digitalSTROM system.

## vDC vs. Native dSD Devices

### Similarities

- Appear identical in dSS configurator UI
- Support same scenes and groups
- Have dSUIDs
- Can be assigned to zones and groups
- Support property queries
- Execute scene calls

### Differences

| Aspect | Native dSD | vdSD (via vDC) |
|--------|-----------|----------------|
| **Communication** | dS485 powerline | TCP/IP network |
| **Discovery** | Automatic on circuit | Avahi/Bonjour |
| **Latency** | Very low (~ms) | Low (~10-100ms) |
| **Power** | From circuit | Independent |
| **Reliability** | Circuit-bound | Network-dependent |
| **Protocol** | dS485 binary | Protobuf over TCP |

## Development Options

### Option 1: libdsvdc (C Library)

**Best For:** Device types 1 & 2 (single devices or device-side vDC)

**Features:**
- Lightweight C library
- Minimal dependencies
- Suitable for embedded systems
- Low-level, more control

**Resources:**
🔍 **MISSING**: Link to libdsvdc repository

### Option 2: vdcd (C++ Framework)

**Best For:** Type 3 (gateway devices)

**Features:**
- Full-featured framework
- Built-in device class support
- Abstracts vDC API complexity
- Extensive feature set

**Resources:**
🔍 **MISSING**: Link to vdcd repository

### Option 3: Custom Implementation

**Best For:** Any type, specific requirements, other languages

**Features:**
- Complete flexibility
- Any language with protobuf support
- Use this documentation + proto file
- More development effort

## Licensing

vDC code and implementations:

- **GPL V3**: Open source implementations
- **Commercial Licenses**: Available from digitalSTROM AG

Please contact digitalSTROM AG for:
- Commercial licensing
- Integration support
- Certification requirements

## Best Practices

### 1. Proper dSUID Generation

- Must be unique across entire dS ecosystem
- Use deterministic generation based on hardware IDs
- Never reuse dSUIDs
- Document your dSUID generation scheme

### 2. Robust Reconnection

- Handle network disconnections gracefully
- Re-announce all devices after reconnect
- Restore session state
- Implement exponential backoff for reconnection attempts

### 3. Property Implementation

- Implement all required common properties
- Return empty for unsupported optional properties (don't error)
- Keep property values current
- Use push notifications for state changes

### 4. Scene Handling

- Store scene values persistently
- Support all relevant group scenes
- Respond quickly to scene calls
- Handle unknown scenes gracefully

### 5. Error Handling

- Use appropriate error codes
- Provide helpful error descriptions
- Log errors for debugging
- Don't crash on unexpected messages

## What's Next?

- **[Communication Protocol](06-protocol.md)** - Detailed protocol specification
- **[API Messages](07-api-messages.md)** - Complete message reference
- **[Session Management](11-session-management.md)** - Implementing sessions
- **[Device Integration](12-device-integration.md)** - Detailed integration guide

---

**Related Documents:**
- [Introduction](01-introduction.md) - vDC basics
- [Core Concepts](03-core-concepts.md) - digitalSTROM fundamentals
