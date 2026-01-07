# Core Concepts

This document explains the fundamental concepts of the digitalSTROM system that are essential for understanding the vDC API.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Data Model](#data-model)
3. [Structure Objects](#structure-objects)
4. [Application Groups and Colors](#application-groups-and-colors)
5. [Scenes](#scenes)
6. [Unique Identifiers](#unique-identifiers)
7. [Events and Information Flow](#events-and-information-flow)

## System Architecture

### Logical vs. Physical Structure

digitalSTROM has two parallel structures:

**Logical Structure:**
- **Apartment**: The entire digitalSTROM installation
- **Zones**: User-defined logical spaces (typically rooms)
- **Groups**: Devices grouped by application type (lights, blinds, etc.)
- **Areas**: Subsets within a group
- **Clusters**: User-defined device collections

**Physical Structure:**
- **Installation**: All physical digitalSTROM equipment
- **Circuits**: Power line segments
- **IP Network**: Network infrastructure for IP-based devices

### How They Relate

```
Physical:    Building
                │
        ┌───────┴───────┐
        │               │
    Circuits        IP Network
        │               │
     dSM/dSD         vDC/vdSD

Logical:    Apartment
                │
        ┌───────┴───────┐
        │               │
      Zones           Groups
      (Rooms)      (Applications)
        │               │
     Devices         Devices
```

## Data Model

### Zones (Rooms)

A **Zone** represents a physical space in the building, typically a room.

**Characteristics:**
- Defined by users during configuration
- Usually corresponds to physical rooms
- Each zone has a unique Zone ID
- Devices are assigned to zones
- Special Zone 0 = "outside building" or "unassigned"

**Example Zones:**
- Living Room (Zone ID: 1)
- Kitchen (Zone ID: 2)
- Bedroom (Zone ID: 3)

### Groups (Application Types)

**Groups** organize devices by their function, regardless of physical location.

Each group represents an application type and has an associated color for easy identification.

## Application Groups and Colors

digitalSTROM uses color coding to represent different application types:

| Group ID | Name | Color | Application Examples |
|----------|------|-------|---------------------|
| 1 | Light | Yellow | Room lights, garden lights, building illumination |
| 2 | Blinds | Gray | Blinds, shades, awnings, curtains |
| 3 | Heating | Blue | Heating systems |
| 8 | Joker | Black | Generic/multi-function devices |
| 9 | Cooling | Blue | Cooling, air conditioning |
| 10 | Ventilation | Blue | Ventilation systems |
| 11 | Window | Blue | Automated windows |
| 12 | Recirculation | Blue | Air recirculation |
| 4 | Audio | Cyan | Music systems, radio |
| 5 | Video | Magenta | TV, video systems |
| 6 | Security | Red | Alarms, fire, panic buttons |
| 7 | Access | Green | Doors, doorbells, access control |
| 48 | Single Devices | White | Appliances (refrigerator, coffee maker, etc.) |

### Special Groups

- **Group 0 (Standard/Broadcast)**: All devices in a zone
- **Group 8 (Joker/Black)**: Multi-functional devices that can be reconfigured

## Scenes

**Scenes** are pre-configured states that control one or more devices simultaneously. They are central to digitalSTROM's operation.

### Scene Categories

#### 1. Function and Group-Related Scenes

These scenes are specific to application groups:

**Basic Presets (Scenes 1-4):**
- Scene 0: Turn off / minimum value
- Scene 5: Turn on / maximum value  
- Scene 1-4: User-programmable presets

**Stepping Scenes (Scenes 12-14):**
- Scene 12: Decrement (dim down, lower blinds)
- Scene 13: Increment (dim up, raise blinds)
- Scene 14: Stop (stop at current position)

**Example for Lights:**
- Scene 0: Off
- Scene 1: Preset 1 (e.g., 30% brightness)
- Scene 2: Preset 2 (e.g., 60% brightness)
- Scene 3: Preset 3 (e.g., 80% brightness)
- Scene 4: Preset 4 (e.g., reading light)
- Scene 5: Full on (100% brightness)

#### 2. Area Scenes (Scenes 15-18)

Control subsets of devices within a group:
- Scene 15-18: Area presets 1-4

#### 3. Local Pushbutton Scenes

- Scene 32-40: Local priority scenes

#### 4. Temperature Control Scenes

For heating/cooling applications:
- Scene 50-53: Comfort settings
- Scene 54-57: Economy settings
- Scene 58-62: Temperature operation modes

#### 5. Group-Independent Scenes (64-126)

These scenes affect all devices regardless of group:

**System State Scenes:**
- Scene 64: Deep Off (everything off, minimum power)
- Scene 65: Standby (reduced power mode)
- Scene 67: Sleeping (night mode)
- Scene 68: Wakeup (morning activation)
- Scene 69: Present (someone is home)
- Scene 70: Absent (nobody home)
- Scene 71: Door Bell
- Scene 72: Panic (emergency)
- Scene 73: Fire (fire alarm)
- Scene 74: Smoke (smoke alarm)
- Scene 75: Water (water alarm)
- Scene 76: Gas (gas alarm)
- Scene 77-82: Weather-related (wind, rain, hail)
- Scene 83: Burglary alarm
- Scene 84: Zone Active

### Scene Calling

Scenes can be called:
- **By Group**: Affects devices in a specific group (e.g., "turn on all lights")
- **By Zone**: Affects all groups in a zone (e.g., "activate scene in living room")
- **By Device**: Affects a specific device
- **Globally**: Affects the entire installation (e.g., "panic" scene)

### Scene Storage

- Each device stores scene values locally
- Scene values can be modified via "Save Scene" action
- Devices recall stored values when scene is called

## Unique Identifiers

### dSUID - digitalSTROM Unique Identifier

Every entity in digitalSTROM has a **dSUID**:

**Format:**
- 17 bytes (136 bits)
- Represented as 34 hexadecimal characters
- Example: `198C033E330755E78015F97AD093DD1C00`

**What Has a dSUID:**
- Every device (dSD, vdSD)
- Every logical vDC
- Every vDC host
- Every vdSM
- Meters, circuits, zones

### dSID - Device Serial ID

Different from dSUID, the **dSID** is based on RFID standards:

**Formats:**
- **SGTIN-96**: Standard identifier for physical devices
- **GID-96**: Generic identifier
- **SGTIN-128**: Extended format with serial number

**Components:**
- Company Prefix (identifies manufacturer)
- Item Reference (product model)
- Serial Number (individual device)

### ModelUID

The **modelUID** is a system-wide identifier for functionally identical devices:

- Devices with the same functionality have the same modelUID
- Different hardware with same dS function = same modelUID
- Same hardware with different dS function = different modelUID

**Example:**
- Two identical hardware switches, one configured as button, one as binary input → different modelUIDs

### Hardware Identifiers

**hardwareGuid**: Globally unique hardware identifier in URN format

Formats include:
- `gs1:(01)ggggg(21)sssss` - GS1 GTIN + serial
- `macaddress:MMMMM` - MAC Address
- `enoceanaddress:XXXXXXXX` - EnOcean device address
- `uuid:UUUUUUU` - UUID

**hardwareModelGuid**: Hardware model identifier

- `gs1:(01)ggggg` - GS1 GTIN  
- `enoceaneep:oofftt` - EnOcean Equipment Profile

## Events and Information Flow

### Event Levels

digitalSTROM processes events at three levels:

#### 1. Device Level
- Button presses
- Binary input changes
- Sensor readings
- Local device events

#### 2. System Level
- dS485 protocol messages (powerline devices)
- vDC-API messages (virtual devices)
- Inter-device communication

#### 3. High Level (Application Level)
- Scene calls
- Automation rules
- User interface actions
- Cloud service integrations

### Information Flow

```
┌──────────────┐
│   User/App   │
└──────┬───────┘
       │
┌──────▼────────┐
│      dSS      │  High Level
└──────┬────────┘  (Orchestration)
       │
┌──────▼────────┐
│  dSM / vdSM   │  System Level
└──────┬────────┘  (Protocol)
       │
┌──────▼────────┐
│  dSD / vdSD   │  Device Level
│   (Devices)   │  (Hardware)
└───────────────┘
```

### Distributed Intelligence

digitalSTROM uses **distributed intelligence**:

- **Devices are intelligent**: Each device can execute scenes locally
- **No single point of failure**: System continues working even if dSS fails
- **Fast response**: Scene execution doesn't require round-trip to server
- **Resilient**: Basic functions work even with network issues

**Example:**
When you press a wall switch:
1. Switch sends event to circuit (immediate)
2. Other devices on circuit respond directly (milliseconds)
3. Event also propagates to dSM/dSS for logging and automation
4. System-wide reactions execute (if configured)

## Operating Principles

### Scene-Centric Design

digitalSTROM is fundamentally scene-based rather than device-based:

- Users think in scenes ("movie mode") not device commands ("dim living room lights to 30%")
- Scenes are pre-configured and can be complex
- Simple triggers execute complex behaviors

### Local Priority

Devices support **local priority** - when a user manually overrides a device:

- Device remembers this is a local override
- Automated scenes don't override local changes
- Priority times out after configured period
- Scene 32 (Set Local Priority) activates this mode

### Group Coordination

Devices in the same group coordinate behavior:

- Light group devices dim together
- Blind group devices move in unison
- Heating group maintains zone temperature

## Key Takeaways for vDC Implementation

When implementing a vDC, remember:

1. **Devices must support scenes** - Store and recall scene values
2. **Group membership matters** - Determines which notifications your device receives
3. **Zone assignment required** - Every device belongs to a zone
4. **dSUIDs must be unique** - Generate proper unique identifiers
5. **Properties describe capabilities** - Use properties to declare what your device can do
6. **Events flow both ways** - Your device sends state changes and receives commands

## What's Next?

- **[vDC Overview](04-vdc-overview.md)** - Detailed system architecture
- **[vDC Overview](04-vdc-overview.md)** - How vDC fits into digitalSTROM
- **[Core Concepts](03-core-concepts.md)** - Detailed scene implementation guide

---

**Related:**
- [Glossary](09-glossary.md) - Complete terminology reference
- [Properties System](07-properties.md) - How properties work
