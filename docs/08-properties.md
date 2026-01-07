# Properties System

The vDC API uses a hierarchical, named property system to describe device capabilities, configuration, and state.

## Property Basics

### What Are Properties?

**Properties** are named values organized in a tree structure that describe:
- Device capabilities (what the device can do)
- Device configuration (how the device is configured)
- Device state (current status and values)
- Metadata (manufacturer, model, version, etc.)

### Property Structure

Properties form a **tree hierarchy**, similar to a filesystem or JSON structure:

```
device (root)
├─ dSUID: "123456..."
├─ name: "Living Room Light"
├─ model: "SmartBulb v2"
├─ output
│  ├─ value: 75.0
│  └─ mode: 1
└─ scenes
   ├─ scene[0]
   │  └─ value: 0.0
   └─ scene[5]
      └─ value: 100.0
```

### Access Control

Each property has access control:

| Access | Symbol | Meaning |
|--------|--------|---------|
| Read-only | `r` | Can be read via getProperty |
| Read-write | `r/w` | Can be read and written |
| Write-only | `w` | Can only be written (rare) |

## Common Properties

These properties are supported by all addressable entities (devices, vDCs, vDC hosts):

### Identification Properties

| Property | Type | Access | Description |
|----------|------|--------|-------------|
| `dSUID` | string | r | 34-character hex dSUID of the entity |
| `type` | string | r | Entity type: "vdSD", "vDC", "vDChost", "vdSM" |
| `displayId` | string | r | Human-readable ID printed on physical device |
| `name` | string | r/w | User-assigned name of the entity |

**Example:**
```python
{
    "dSUID": "198C033E330755E78015F97AD093DD1C00",
    "type": "vdSD",
    "displayId": "SN-12345",
    "name": "Living Room Light"
}
```

### Model Properties

| Property | Type | Access | Description |
|----------|------|--------|-------------|
| `model` | string | r | Human-readable model name |
| `modelUID` | string | r | System-unique ID for functional model |
| `modelVersion` | string | r (opt) | Model version (firmware version) |
| `deviceClass` | string | r (opt) | Device class profile name (e.g., "Light") |
| `deviceClassVersion` | string | r (opt) | Device class profile version |

**Example:**
```python
{
    "model": "WiFi Smart Bulb Pro",
    "modelUID": "com.example.smartbulb.wifi.v2",
    "modelVersion": "2.1.5",
    "deviceClass": "Light",
    "deviceClassVersion": "1.0"
}
```

### Hardware Properties

| Property | Type | Access | Description |
|----------|------|--------|-------------|
| `hardwareGuid` | string | r (opt) | Hardware instance GUID in URN format |
| `hardwareModelGuid` | string | r (opt) | Hardware model GUID in URN format |
| `hardwareVersion` | string | r (opt) | Hardware version string |

**GUID Formats:**
- `gs1:(01)gtin(21)serial` - GS1 GTIN + serial number
- `macaddress:AABBCCDDEEFF` - MAC Address
- `enoceanaddress:01234567` - EnOcean device address (8 hex digits)
- `uuid:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` - UUID
- `gs1:(01)gtin` - GS1 GTIN (for model GUID)
- `enoceaneep:RRFFTT` - EnOcean Equipment Profile

**Example:**
```python
{
    "hardwareGuid": "macaddress:001122334455",
    "hardwareModelGuid": "gs1:(01)04050300870342",
    "hardwareVersion": "1.2"
}
```

### Vendor Properties

| Property | Type | Access | Description |
|----------|------|--------|-------------|
| `vendorName` | string | r (opt) | Manufacturer/vendor name |
| `vendorGuid` | string | r (opt) | Vendor GUID in URN format |
| `oemGuid` | string | r (opt) | OEM product GUID |
| `oemModelGuid` | string | r (opt) | OEM product model GUID (GTIN) |

**Vendor GUID Formats:**
- `enoceanvendor:XXX[:name]` - EnOcean vendor ID (3 hex digits) + optional name
- `vendorname:CompanyName` - Clear text vendor name
- `gs1:(412)gln` - GS1 Global Location Number

### UI Properties

| Property | Type | Access | Description |
|----------|------|--------|-------------|
| `configURL` | string | r (opt) | Full URL to device web configuration |
| `deviceIcon16` | binary | r (opt) | 16x16 PNG icon for UI display |
| `deviceIconName` | string | r (opt) | Filename-safe icon name for caching |

### Status Properties

| Property | Type | Access | Description |
|----------|------|--------|-------------|
| `active` | boolean | r (opt) | Device is operational (true) or has issues (false) |

**Important:** When `active` changes, vDC should send push notification.

## Device-Specific Properties

⚠️ **INCOMPLETE**: Full device property specification would be very long. Key categories:

### Output Properties

For devices with output capabilities (lights, blinds, etc.):

| Property Path | Type | Description |
|---------------|------|-------------|
| `output.value` | double | Current output value (0.0-100.0 typically) |
| `output.mode` | integer | Output mode |
| `output.targetValue` | double | Target value (if transitioning) |

### Channel Properties

For devices with multiple channels:

| Property Path | Type | Description |
|---------------|------|-------------|
| `channelStates[i].channelId` | string | Channel identifier |
| `channelStates[i].value` | double | Current channel value |
| `channelStates[i].channelType` | string | Channel type (e.g., "brightness", "hue") |

### Scene Properties

Scene values stored per device:

| Property Path | Type | Description |
|---------------|------|-------------|
| `scenes[i].sceneNo` | integer | Scene number (0-126) |
| `scenes[i].value` | double | Stored scene value |
| `scenes[i].dontCare` | boolean | Whether device ignores this scene |

### Sensor Properties

For devices with sensors:

| Property Path | Type | Description |
|---------------|------|-------------|
| `sensors[i].sensorType` | string | Type of sensor |
| `sensors[i].value` | double | Current sensor reading |
| `sensors[i].unit` | string | Unit of measurement |

## Property Access

### Reading Properties

Use `VDSM_REQUEST_GET_PROPERTY` to read properties:

**Request:**
```python
msg = Message()
msg.type = Type.VDSM_REQUEST_GET_PROPERTY
msg.message_id = 42
msg.vdsm_request_get_property.dSUID = device_dsuid

# Query specific properties
query1 = PropertyElement()
query1.name = "dSUID"
msg.vdsm_request_get_property.query.append(query1)

query2 = PropertyElement()
query2.name = "name"
msg.vdsm_request_get_property.query.append(query2)

# Query nested property
query3 = PropertyElement()
query3.name = "output"
child = PropertyElement()
child.name = "value"
query3.elements.append(child)
msg.vdsm_request_get_property.query.append(query3)
```

**Response:**
```python
# VDC_RESPONSE_GET_PROPERTY
response.vdc_response_get_property.properties = [
    PropertyElement(name="dSUID", value=PropertyValue(v_string="123...")),
    PropertyElement(name="name", value=PropertyValue(v_string="Light 1")),
    PropertyElement(
        name="output",
        elements=[
            PropertyElement(name="value", value=PropertyValue(v_double=75.0))
        ]
    )
]
```

### Writing Properties

Use `VDSM_REQUEST_SET_PROPERTY` to write properties:

**Request:**
```python
msg = Message()
msg.type = Type.VDSM_REQUEST_SET_PROPERTY
msg.message_id = 43
msg.vdsm_request_set_property.dSUID = device_dsuid

# Set property value
prop = PropertyElement()
prop.name = "name"
prop.value = PropertyValue()
prop.value.v_string = "New Name"
msg.vdsm_request_set_property.properties.append(prop)
```

**Response:**
```python
# GenericResponse
response.generic_response.code = ERR_OK
# or error code if failed
```

### Partial Property Queries

You can query entire subtrees:

```python
# Query entire "output" subtree
query = PropertyElement()
query.name = "output"
# Don't specify children - returns all children
```

Returns:
```python
PropertyElement(
    name="output",
    elements=[
        PropertyElement(name="value", value=...),
        PropertyElement(name="mode", value=...),
        PropertyElement(name="targetValue", value=...),
        # ... all output properties
    ]
)
```

### Missing Properties

**Important Behavior:**
- `getProperty` for non-existent property: Returns empty (no error)
- `setProperty` for non-existent property: Returns error

```python
# Reading non-existent property
response = get_property(device, "nonExistent")
# response.properties will be empty, but no error

# Writing non-existent property
response = set_property(device, "nonExistent", value)
# response.code == ERR_NOT_FOUND
```

## Push Notifications

When device state changes, vDC can proactively push updates:

```python
msg = Message()
msg.type = Type.VDC_SEND_PUSH_NOTIFICATION
msg.vdc_send_push_notification.dSUID = device_dsuid

# Changed property
prop = PropertyElement()
prop.name = "output"
child = PropertyElement()
child.name = "value"
child.value = PropertyValue()
child.value.v_double = 50.0
prop.elements.append(child)

msg.vdc_send_push_notification.changedproperties.append(prop)
```

**When to Push:**
- Output value changes (user changes light brightness)
- Sensor value changes (temperature reading updates)
- Device becomes active/inactive
- Configuration changes
- Error states

**When NOT to Push:**
- In response to vdSM commands (they already know)
- For every tiny change (batch or threshold)
- Too frequently (rate limiting)

## Best Practices

### 1. Implement Required Properties

Always implement these common properties:
- `dSUID`
- `type`
- `model`
- `modelUID`
- `name`
- `deviceClass` (for devices)

### 2. Optional Properties

Return empty for unsupported optional properties:
```python
if property_name == "configURL" and not self.has_web_config:
    # Don't return this property at all
    return None
```

### 3. Property Naming

- Use camelCase for property names
- Be consistent with standard property names
- Don't invent new names for standard concepts

### 4. Value Types

Use appropriate PropertyValue type:
- Strings: Use `v_string`
- Integers: Use `v_int64` (not `v_uint64` unless truly unsigned)
- Floats: Use `v_double`
- Booleans: Use `v_bool`
- Binary data: Use `v_bytes`

### 5. Property Caching

Cache property values to avoid repeated computation:
```python
class Device:
    def __init__(self):
        self._property_cache = {}
    
    def get_property(self, name):
        if name not in self._property_cache:
            self._property_cache[name] = self._compute_property(name)
        return self._property_cache[name]
    
    def invalidate_cache(self, name):
        if name in self._property_cache:
            del self._property_cache[name]
```

## Common Pitfalls

### 1. Wrong PropertyValue Type

```python
# WRONG - using wrong type
value = PropertyValue()
value.v_string = "75"  # Storing number as string

# CORRECT
value = PropertyValue()
value.v_double = 75.0
```

### 2. Not Handling Optional Properties

```python
# WRONG - error on missing optional property
if property_name == "configURL":
    if not self.config_url:
        return Error("Not found")

# CORRECT - just don't return it
if property_name == "configURL":
    if not self.config_url:
        return None  # Omit from response
    return PropertyElement(name="configURL", value=...)
```

### 3. Modifying Read-Only Properties

```python
# WRONG - allowing write to read-only property
if property_name == "dSUID":
    self.dsuid = new_value  # dSUID is read-only!

# CORRECT - return error
if property_name == "dSUID":
    return Error(ERR_FORBIDDEN, "dSUID is read-only")
```

## What's Next?

- **[API Messages](07-api-messages.md)** - Using properties in messages
- **[Protocol Buffers](09-protobuf-reference.md)** - PropertyElement structure
- **[Device Integration](12-device-integration.md)** - Implementing device properties

---

**Related:**
- [Core Concepts](03-core-concepts.md) - Understanding device model
- [Error Handling](10-error-handling.md) - Property access errors
