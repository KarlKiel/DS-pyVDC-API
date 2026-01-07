# Glossary

Complete terminology reference for the digitalSTROM vDC API.

## A

### Apartment
The logical instance of a complete digitalSTROM installation, including all rooms and devices.

### API Version
Version number of the vDC API protocol, negotiated during session initialization. Current version is 3.

### Application Group
See [Group](#group).

### Application Type
Categories of device functionality (lights, blinds, heating, etc.), each associated with a color group.

### Area
A subset of devices within an Application Group. Areas are only supported for Lights (Yellow) and Blinds (Gray) groups. Devices in an area can be controlled separately from the rest of the group.

### Avahi
GNU implementation of Apple's Bonjour/mDNS service discovery protocol, used for vDC host discovery on Linux systems.

## B

### Bonjour
Apple's implementation of mDNS/DNS-SD service discovery, equivalent to Avahi on non-Apple platforms.

### Building
The physical structure containing the Installation. May differ from Apartment in terms of ownership or logical boundaries.

## C

### Circuit
A physical power line segment in the building's electrical installation. Native dSD devices communicate over circuits using dS485 protocol.

### Cluster
User-defined logical grouping of devices across zones, based on Application Type. Unlike Groups, Clusters are custom collections that can span multiple rooms.

## D

### Device Class
A standardized device profile defined by digitalSTROM, specifying device capabilities and behaviors (e.g., "Light", "Shade", "Heating").

### Device Class Version
Revision number of a device class profile specification.

### Distributed Intelligence
digitalSTROM's architectural approach where control logic is distributed across devices rather than centralized, enabling local operation even if the server is unavailable.

### dS485
Proprietary powerline communication protocol used by native digitalSTROM devices on electrical circuits.

### dSID (digitalSTROM ID)
Device serial identifier based on RFID standards (SGTIN-96, SGTIN-128, or GID-96), different from dSUID.

### dSM (digitalSTROM Meter)
Physical hardware device that manages communication on a power circuit, serving as a bridge between dS485 powerline protocol and the dSS.

### dSS (digitalSTROM Server)
Central server component providing configuration, management, automation, and user interface for the digitalSTROM installation.

### dSD (digitalSTROM Device)
Physical terminal block device that communicates via dS485 powerline protocol.

### dSUID (digitalSTROM Unique Identifier)
A unique 17-byte (136-bit) identifier represented as 34 hexadecimal characters. Every entity in digitalSTROM (devices, vDCs, meters, etc.) has a dSUID.

**Format Example:** `198C033E330755E78015F97AD093DD1C00`

## E

### EnOcean
Wireless energy-harvesting radio protocol, commonly bridged to digitalSTROM via gateway vDCs.

## G

### Gateway
A vDC host (Type 3) that bridges other protocols or bus systems to digitalSTROM, allowing integration of devices using technologies like EnOcean, DALI, Zigbee, etc.

### GenericResponse
Protocol buffer message type used to communicate operation results, especially errors. Contains error codes, error types, and descriptions.

### GID-96
Global Identifier 96-bit format, one of the RFID-based identifier formats used for dSID.

### Group
Collection of devices organized by Application Type (function), independent of physical location. Groups have associated colors and standardized behaviors.

**Examples:** Group 1 (Yellow/Lights), Group 2 (Gray/Blinds), Group 3 (Blue/Heating)

### GTIN (Global Trade Item Number)
GS1 standard product identifier, used in hardwareModelGuid and oemModelGuid properties.

## H

### hardwareGuid
Globally unique identifier for a physical device instance, in URN format (e.g., `gs1:(01)ggggg(21)sssss` or `macaddress:MMMMM`).

### hardwareModelGuid
Globally unique identifier for a hardware model, in URN format (e.g., `gs1:(01)ggggg` for GS1 GTIN).

## I

### Installation
All physical digitalSTROM equipment in a building or apartment, including meters, devices, and network components.

### IP Network
TCP/IP network infrastructure used for communication with virtual devices (vDCs) and the dSS.

## L

### libdsvdc
Lightweight C library for implementing vDC hosts, targeted at device-side vDCs (Type 1 & 2 integrations).

### Local Priority
State where a device has been manually overridden by the user and should not be automatically controlled until the priority timeout expires or is cleared.

## M

### Message ID
Unique identifier for each message in the vDC protocol, used to match responses with requests. Typically incremented for each new request.

### modelGuid / modelUID
System-wide unique identifier for a functional device model. Devices with identical digitalSTROM functionality share the same modelUID, even if hardware differs.

## N

### Notification
One-way message that doesn't expect a response (except in error cases). Used for scene calls, dimming commands, and similar actions where acknowledgment is not required.

## O

### oemGuid
Globally unique identifier for the product a device is embedded in (Original Equipment Manufacturer identifier).

### oemModelGuid
GTIN-format identifier for the OEM product model.

## P

### Preset
See [Scene](#scene).

### Property
Named value in the vDC API property system. Properties form a hierarchical tree structure describing device capabilities, configuration, and state.

### PropertyElement
Protocol buffer message containing a property name, value, and optionally child elements (for tree structure).

### PropertyValue
Protocol buffer message containing a typed value (bool, uint64, int64, double, string, or bytes).

### Protocol Buffers (protobuf)
Google's language-neutral, platform-neutral serialization format used as the encoding method for vDC API messages.

## R

### Request
Message that expects a specific response. Contains a message_id for response matching.

### ResultCode
Enumeration of error codes in GenericResponse (ERR_OK, ERR_NOT_FOUND, etc.).

## S

### Scene
Pre-configured state or action that can be called to control devices. Scenes are identified by numbers (0-126) and may be group-specific or global.

**Examples:**
- Scene 0: Off/Minimum
- Scene 5: On/Maximum
- Scene 1-4: User presets
- Scene 64: Deep Off
- Scene 72: Panic

### Send Message
Message type that only expects an error response if something goes wrong. No response sent on success.

### Session
Logical connection between vdSM and vDC host, tied to the lifetime of the TCP connection. When connection breaks, session ends.

### SGTIN-96
Serialized Global Trade Item Number, 96-bit format based on EPC RFID standards, used for device identification (dSID).

### SGTIN-128
Extended 128-bit version of SGTIN with serial number.

## T

### TCP
Transmission Control Protocol - transport layer used for vDC API communication over IP networks.

## V

### vDC (Virtual Device Connector)
Logical software entity representing a class or type of external devices. Has its own dSUID. Multiple vDCs can exist on one vDC host.

### vDC API
Application Programming Interface for integrating IP-based devices into digitalSTROM via virtual device connectors.

### vDC Host
Physical or virtual network device offering a TCP server socket for vdSM connections. Can host multiple logical vDCs.

### vDC Session
See [Session](#session).

### vdcd
C++ framework for implementing vDC hosts, particularly suited for gateway devices (Type 3 integrations).

### vdSD (Virtual digitalSTROM Device)
Single virtual device represented in the digitalSTROM system through a vDC. Appears and behaves like a native dSD device.

### vdSM (Virtual digitalSTROM Meter)
Software component (typically running on dSS) that acts as a client, connecting to vDC hosts to integrate virtual devices into the system.

### vendorGuid
Globally unique identifier for the device vendor/manufacturer in URN format.

### vendorId
See [vendorGuid](#vendorguid).

## Z

### Zone
Logical representation of a physical space (typically a room) in the building. Devices are assigned to zones for organization and control.

**Special Zones:**
- Zone 0: Outside building or unassigned

---

## Abbreviations

| Abbreviation | Meaning |
|--------------|---------|
| API | Application Programming Interface |
| ARQ | Automatic Repeat Query |
| DALI | Digital Addressable Lighting Interface |
| EPC | Electronic Product Code |
| GID | Global Identifier |
| GPL | GNU General Public License |
| GS1 | Global Standards One (organization) |
| GTIN | Global Trade Item Number |
| GUID | Globally Unique Identifier |
| JSON | JavaScript Object Notation |
| MAC | Media Access Control |
| mDNS | Multicast DNS |
| OEM | Original Equipment Manufacturer |
| RFID | Radio-Frequency Identification |
| SGTIN | Serialized Global Trade Item Number |
| TCP | Transmission Control Protocol |
| UI | User Interface |
| URN | Uniform Resource Name |
| UUID | Universally Unique Identifier |

---

## Color Group Reference

Quick reference for application group colors:

| Color | Group ID | Application |
|-------|----------|-------------|
| Yellow | 1 | Lights |
| Gray | 2 | Blinds/Shades |
| Blue | 3, 9-12 | Climate (Heating, Cooling, Ventilation, Windows) |
| Cyan | 4 | Audio |
| Magenta | 5 | Video |
| Red | 6 | Security |
| Green | 7 | Access |
| Black | 8 | Joker (multi-function) |
| White | 48 | Single Devices |

---

## Related Documents

- **[Core Concepts](03-core-concepts.md)** - Fundamental concepts explained
- **[Introduction](01-introduction.md)** - System overview
- **[vDC Overview](05-vdc-overview.md)** - Virtual device connector details
