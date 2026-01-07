# Protocol Buffers Reference

This document describes the Protocol Buffer message definitions used in the vDC API, based on `genericVDC.proto`.

## Protocol Buffer Basics

The vDC API uses **Protocol Buffers v2** syntax for message encoding.

### Why Protocol Buffers?

- **Efficient**: Binary encoding, smaller than JSON/XML
- **Typed**: Strong type checking
- **Versioned**: Forward and backward compatible
- **Language-neutral**: Supported in many languages
- **Fast**: Quick serialization/deserialization

### Message Framing

Messages are sent over TCP with a 2-byte length header:

```
┌─────────────┬────────────────────┐
│ Length (2B) │  Protobuf Message  │
│ (uint16_t)  │   (variable size)  │
│ Big-endian  │                    │
└─────────────┴────────────────────┘
```

**Maximum message size:** 16384 bytes (16 KB)

## Message Envelope

All messages are wrapped in the `Message` container:

```protobuf
message Message {
    required Type type = 1 [default = GENERIC_RESPONSE];
    optional uint32 message_id = 2 [default = 0];
    optional GenericResponse generic_response = 3;
    
    // Specific message types (fields 100-123)
    ...
}
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `type` | Type enum | Identifies which message type this is |
| `message_id` | uint32 | Unique ID for request/response matching (0 for unsolicited) |
| `generic_response` | GenericResponse | Error response (if type is GENERIC_RESPONSE) |

## Message Types (Type Enum)

### Responses

| Value | Name | Description |
|-------|------|-------------|
| 1 | GENERIC_RESPONSE | Generic success/error response |

### Session Management

| Value | Name | Direction | Description |
|-------|------|-----------|-------------|
| 2 | VDSM_REQUEST_HELLO | vdSM → vDC | Session initialization request |
| 3 | VDC_RESPONSE_HELLO | vDC → vdSM | Session initialization response |
| 14 | VDSM_SEND_BYE | vdSM → vDC | Close session gracefully |

### Presence Monitoring

| Value | Name | Direction | Description |
|-------|------|-----------|-------------|
| 8 | VDSM_SEND_PING | vdSM → vDC | Check if vDC is alive |
| 9 | VDC_SEND_PONG | vDC → vdSM | Response to ping |

### Device Announcement

| Value | Name | Direction | Description |
|-------|------|-----------|-------------|
| 23 | VDC_SEND_ANNOUNCE_VDC | vDC → vdSM | Announce vDC itself |
| 10 | VDC_SEND_ANNOUNCE_DEVICE | vDC → vdSM | Announce a virtual device |
| 11 | VDC_SEND_VANISH | vDC → vdSM | Remove a device |
| 13 | VDSM_SEND_REMOVE | vdSM → vDC | Request device removal |
| 22 | VDC_SEND_IDENTIFY | vDC → vdSM | Request device identification (blink) |

### Property Access

| Value | Name | Direction | Description |
|-------|------|-----------|-------------|
| 4 | VDSM_REQUEST_GET_PROPERTY | vdSM → vDC | Read property values |
| 5 | VDC_RESPONSE_GET_PROPERTY | vDC → vdSM | Property values response |
| 6 | VDSM_REQUEST_SET_PROPERTY | vdSM → vDC | Write property values |
| 7 | VDC_RESPONSE_SET_PROPERTY | vDC → vdSM | Write confirmation (GenericResponse) |
| 12 | VDC_SEND_PUSH_PROPERTY | vDC → vdSM | Push property changes (deprecated) |

### Notifications (v2c+)

| Value | Name | Direction | Description |
|-------|------|-----------|-------------|
| 26 | VDSM_REQUEST_GENERIC_REQUEST | vdSM → vDC | Generic method call (API v2c+) |

### Device Actions (Notifications from vdSM)

| Value | Name | Description |
|-------|------|-------------|
| 15 | VDSM_NOTIFICATION_CALL_SCENE | Call a scene |
| 16 | VDSM_NOTIFICATION_SAVE_SCENE | Save current value to scene |
| 17 | VDSM_NOTIFICATION_UNDO_SCENE | Undo last scene call |
| 18 | VDSM_NOTIFICATION_SET_LOCAL_PRIO | Activate local priority |
| 19 | VDSM_NOTIFICATION_CALL_MIN_SCENE | Call minimum scene |
| 20 | VDSM_NOTIFICATION_IDENTIFY | Identify device (blink) |
| 21 | VDSM_NOTIFICATION_SET_CONTROL_VALUE | Set a named control value |
| 24 | VDSM_NOTIFICATION_DIM_CHANNEL | Dim/adjust channel (v2+) |
| 25 | VDSM_NOTIFICATION_SET_OUTPUT_CHANNEL_VALUE | Set channel to specific value |

## Message Definitions

### Session Initialization

#### vdsm_RequestHello

```protobuf
message vdsm_RequestHello {
    optional string dSUID = 1;
    optional uint32 api_version = 2;
}
```

**Sent by:** vdSM  
**Purpose:** Initialize vDC session

**Fields:**
- `dSUID`: The vdSM's dSUID (34 hex characters)
- `api_version`: API version the vdSM supports (typically 3)

**Response:** VDC_RESPONSE_HELLO

---

#### vdc_ResponseHello

```protobuf
message vdc_ResponseHello {
    optional string dSUID = 1;
}
```

**Sent by:** vDC  
**Purpose:** Acknowledge session initialization

**Fields:**
- `dSUID`: The vDC host's dSUID

**Error Response:** GenericResponse with ERR_INCOMPATIBLE_API if version not supported

---

### Device Lifecycle

#### vdc_SendAnnounceVdc

```protobuf
message vdc_SendAnnounceVdc {
    optional string dSUID = 1;
}
```

**Sent by:** vDC  
**Purpose:** Announce the vDC itself to the system

**Fields:**
- `dSUID`: The vDC's dSUID (not the vDC host's dSUID)

---

#### vdc_SendAnnounceDevice

```protobuf
message vdc_SendAnnounceDevice {
    optional string dSUID = 1;
    optional string vdc_dSUID = 2;
}
```

**Sent by:** vDC  
**Purpose:** Announce a new virtual device

**Fields:**
- `dSUID`: The device's dSUID
- `vdc_dSUID`: The vDC this device belongs to

---

#### vdc_SendVanish

```protobuf
message vdc_SendVanish {
    optional string dSUID = 1;
}
```

**Sent by:** vDC  
**Purpose:** Remove a device from the system

**Fields:**
- `dSUID`: The device's dSUID to remove

---

### Presence Monitoring

#### vdsm_SendPing

```protobuf
message vdsm_SendPing {
    optional string dSUID = 1;
}
```

**Sent by:** vdSM  
**Purpose:** Check if vDC/device is responsive

**Fields:**
- `dSUID`: Target dSUID to ping (vDC, vDC host, or device)

**Response:** VDC_SEND_PONG (or error if not responsive)

---

#### vdc_SendPong

```protobuf
message vdc_SendPong {
    optional string dSUID = 1;
}
```

**Sent by:** vDC  
**Purpose:** Response to ping

**Fields:**
- `dSUID`: The dSUID that was pinged

---

### Property System

#### PropertyValue

```protobuf
message PropertyValue {
    optional bool v_bool = 1;
    optional uint64 v_uint64 = 2;
    optional int64 v_int64 = 3;
    optional double v_double = 4;
    optional string v_string = 5;
    optional bytes v_bytes = 6;
}
```

**Purpose:** Type-safe value container

**Usage:** Set exactly ONE of the optional fields based on value type.

**Examples:**
- Boolean: `value.v_bool = true`
- Integer: `value.v_int64 = 42`
- String: `value.v_string = "Living Room"`
- Floating: `value.v_double = 23.5`

---

#### PropertyElement

```protobuf
message PropertyElement {
    optional string name = 1;
    optional PropertyValue value = 2;
    repeated PropertyElement elements = 3;
}
```

**Purpose:** Tree-structured property node

**Fields:**
- `name`: Property name (e.g., "dSUID", "name", "output")
- `value`: Property value (leaf nodes)
- `elements`: Child properties (branch nodes)

**Structure:**
```
PropertyElement (name="device")
├─ value: null (has children)
└─ elements:
   ├─ PropertyElement (name="dSUID", value="123...")
   ├─ PropertyElement (name="name", value="Light 1")
   └─ PropertyElement (name="output")
      ├─ value: null (has children)
      └─ elements:
         └─ PropertyElement (name="value", value=75.0)
```

---

#### vdsm_RequestGetProperty

```protobuf
message vdsm_RequestGetProperty {
    optional string dSUID = 1;
    repeated PropertyElement query = 2;
}
```

**Sent by:** vdSM  
**Purpose:** Read property values

**Fields:**
- `dSUID`: Target entity (device, vDC, or vDC host)
- `query`: Property paths to read (can be partial paths)

**Response:** VDC_RESPONSE_GET_PROPERTY

**Example Query:**
```
query[0].name = "dSUID"
query[1].name = "name"
query[2].name = "output"
  query[2].elements[0].name = "value"
```

---

#### vdc_ResponseGetProperty

```protobuf
message vdc_ResponseGetProperty {
    repeated PropertyElement properties = 1;
}
```

**Sent by:** vDC  
**Purpose:** Return requested property values

**Fields:**
- `properties`: Tree of property values

---

#### vdsm_RequestSetProperty

```protobuf
message vdsm_RequestSetProperty {
    optional string dSUID = 1;
    repeated PropertyElement properties = 2;
}
```

**Sent by:** vdSM  
**Purpose:** Write property values

**Fields:**
- `dSUID`: Target entity
- `properties`: Property paths and values to write

**Response:** GenericResponse (VDC_RESPONSE_SET_PROPERTY)

---

### Scene Notifications

#### vdsm_NotificationCallScene

```protobuf
message vdsm_NotificationCallScene {
    repeated string dSUID = 1;
    optional int32 scene = 2;
    optional bool force = 3;
    optional int32 group = 4;
    optional int32 zone_id = 5;
}
```

**Sent by:** vdSM  
**Purpose:** Call a scene

**Fields:**
- `dSUID`: List of devices to call scene on
- `scene`: Scene number (0-126)
- `force`: Force execution even if device has local priority
- `group`: Group ID (if group-specific scene)
- `zone_id`: Zone ID (if zone-wide scene)

**Response:** None (notification)

---

#### vdsm_NotificationSaveScene

```protobuf
message vdsm_NotificationSaveScene {
    repeated string dSUID = 1;
    optional int32 scene = 2;
    optional int32 group = 3;
    optional int32 zone_id = 4;
}
```

**Sent by:** vdSM  
**Purpose:** Save current device state to scene

**Fields:**
- `dSUID`: Devices to save state from
- `scene`: Scene number to save to
- `group`: Group ID
- `zone_id`: Zone ID

---

#### vdsm_NotificationUndoScene

```protobuf
message vdsm_NotificationUndoScene {
    repeated string dSUID = 1;
    optional int32 scene = 2;
    optional int32 group = 3;
    optional int32 zone_id = 4;
}
```

**Sent by:** vdSM  
**Purpose:** Undo last scene call, restore previous state

---

### Channel Control

#### vdsm_NotificationDimChannel

```protobuf
message vdsm_NotificationDimChannel {
    repeated string dSUID = 1;
    optional int32 channel = 2;
    optional int32 mode = 3;
    optional int32 area = 4;
    optional int32 group = 5;
    optional int32 zone_id = 6;
    optional string channelId = 7; // API v3+
}
```

**Sent by:** vdSM  
**Purpose:** Start/stop dimming a channel

**Fields:**
- `dSUID`: Target devices
- `channel`: Channel number (deprecated, use channelId)
- `mode`: Dim mode (0=stop, 1=up, -1=down)
- `area`: Area ID
- `group`: Group ID
- `zone_id`: Zone ID
- `channelId`: Channel identifier string (API v3+)

---

#### vdsm_NotificationSetOutputChannelValue

```protobuf
message vdsm_NotificationSetOutputChannelValue {
    repeated string dSUID = 1;
    optional bool apply_now = 2 [default = true];
    optional int32 channel = 3;
    optional double value = 4;
    optional string channelId = 5; // API v3+
}
```

**Sent by:** vdSM  
**Purpose:** Set channel to specific value

**Fields:**
- `dSUID`: Target devices
- `apply_now`: Apply immediately (true) or stage for later (false)
- `channel`: Channel number (deprecated)
- `value`: Target value (0.0-100.0 typically)
- `channelId`: Channel identifier (API v3+)

---

### Other Notifications

#### vdsm_NotificationIdentify

```protobuf
message vdsm_NotificationIdentify {
    repeated string dSUID = 1;
    optional int32 group = 2;
    optional int32 zone_id = 3;
}
```

**Sent by:** vdSM  
**Purpose:** Request device to identify itself (blink, beep, etc.)

---

#### vdsm_NotificationSetControlValue

```protobuf
message vdsm_NotificationSetControlValue {
    repeated string dSUID = 1;
    optional string name = 2;
    optional double value = 3;
    optional int32 group = 4;
    optional int32 zone_id = 5;
}
```

**Sent by:** vdSM  
**Purpose:** Set a named control value

**Fields:**
- `name`: Control name (e.g., "temperature")
- `value`: Control value

---

### Generic Requests (v2c+)

#### vdsm_RequestGenericRequest

```protobuf
message vdsm_RequestGenericRequest {
    optional string dSUID = 1;
    optional string methodname = 2;
    repeated PropertyElement params = 3;
}
```

**Sent by:** vdSM (API v2c+)  
**Purpose:** Generic method invocation on device

**Fields:**
- `dSUID`: Target entity
- `methodname`: Name of method to call
- `params`: Method parameters as property tree

**Response:** GenericResponse

❓ **MISSING**: Complete documentation of available method names and parameters

---

### Error Responses

#### GenericResponse

```protobuf
message GenericResponse {
    required ResultCode code = 1 [default = ERR_OK];
    optional string description = 2;
}
```

**Purpose:** Communicate operation results, especially errors

**Fields:**
- `code`: Error code (see [Error Handling](08-error-handling.md))
- `description`: Human-readable description

**Additional fields** (not in proto, but used in practice):
- `errorType`: Error category for recovery logic
- `userMessageToBeTranslated`: User-facing message

---

### ResultCode Enum

```protobuf
enum ResultCode {
    ERR_OK = 0;
    ERR_MESSAGE_UNKNOWN = 1;
    ERR_INCOMPATIBLE_API = 2;
    ERR_SERVICE_NOT_AVAILABLE = 3;
    ERR_INSUFFICIENT_STORAGE = 4;
    ERR_FORBIDDEN = 5;
    ERR_NOT_IMPLEMENTED = 6;
    ERR_NO_CONTENT_FOR_ARRAY = 7;
    ERR_INVALID_VALUE_TYPE = 8;
    ERR_MISSING_SUBMESSAGE = 9;
    ERR_MISSING_DATA = 10;
    ERR_NOT_FOUND = 11;
    ERR_NOT_AUTHORIZED = 12;
}
```

See [Error Handling](08-error-handling.md) for detailed descriptions.

---

## Message Flow Examples

### Session Initialization

```
vdSM → vDC: Message {
    type = VDSM_REQUEST_HELLO,
    message_id = 1,
    vdsm_request_hello = {
        dSUID = "VDSM_DSUID_HERE",
        api_version = 3
    }
}

vDC → vdSM: Message {
    type = VDC_RESPONSE_HELLO,
    message_id = 1,
    vdc_response_hello = {
        dSUID = "VDC_HOST_DSUID_HERE"
    }
}
```

### Device Announcement

```
vDC → vdSM: Message {
    type = VDC_SEND_ANNOUNCE_VDC,
    message_id = 0,  // Unsolicited
    vdc_send_announce_vdc = {
        dSUID = "VDC_DSUID_HERE"
    }
}

vDC → vdSM: Message {
    type = VDC_SEND_ANNOUNCE_DEVICE,
    message_id = 0,
    vdc_send_announce_device = {
        dSUID = "DEVICE_DSUID_HERE",
        vdc_dSUID = "VDC_DSUID_HERE"
    }
}
```

### Property Read

```
vdSM → vDC: Message {
    type = VDSM_REQUEST_GET_PROPERTY,
    message_id = 2,
    vdsm_request_get_property = {
        dSUID = "DEVICE_DSUID_HERE",
        query = [
            { name = "dSUID" },
            { name = "name" },
            { name = "model" }
        ]
    }
}

vDC → vdSM: Message {
    type = VDC_RESPONSE_GET_PROPERTY,
    message_id = 2,
    vdc_response_get_property = {
        properties = [
            { name = "dSUID", value = { v_string = "DEVICE_DSUID_HERE" } },
            { name = "name", value = { v_string = "Living Room Light" } },
            { name = "model", value = { v_string = "SmartBulb v2" } }
        ]
    }
}
```

### Scene Call

```
vdSM → vDC: Message {
    type = VDSM_NOTIFICATION_CALL_SCENE,
    message_id = 0,  // Notifications use 0
    vdsm_send_call_scene = {
        dSUID = ["DEVICE_DSUID_1", "DEVICE_DSUID_2"],
        scene = 5,  // Scene 5 = "On"
        force = false,
        group = 1,  // Yellow/Lights
        zone_id = 10
    }
}

// No response for notifications
```

## Best Practices

### 1. Message ID Management

- Start at 1, increment for each request
- Use 0 for unsolicited messages (announcements, push notifications)
- Match response message_id to request

### 2. Type Safety in PropertyValue

Always set exactly ONE field:
```python
# Correct
value = PropertyValue()
value.v_string = "test"

# Wrong - don't set multiple fields
value.v_string = "test"
value.v_int64 = 123  # WRONG!
```

### 3. Property Tree Construction

Build trees bottom-up:
```python
# Build child first
child = PropertyElement(name="value", value=PropertyValue(v_double=75.0))

# Then parent
parent = PropertyElement(name="output")
parent.elements.append(child)
```

### 4. Error Checking

Always check for GenericResponse on errors:
```python
if response.type == Type.GENERIC_RESPONSE:
    if response.generic_response.code != ERR_OK:
        handle_error(response.generic_response)
```

## What's Next?

- **[Protocol Buffers Reference](06-protobuf-reference.md)** - Detailed message usage guide
- **[Properties System](07-properties.md)** - Complete property reference
- **[Session Management](05-session-management.md)** - Implementing sessions
- **[Quick Start Guide](02-quickstart.md)** - Complete code examples

---

**Related:**
- [Error Handling](08-error-handling.md) - Error codes and recovery
- [Quick Start](02-quickstart.md) - Basic implementation
