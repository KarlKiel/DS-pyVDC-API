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

This section provides comprehensive device-specific property specifications for virtual digitalSTROM devices (vdSD). These properties extend the common properties and define device capabilities, configuration, and state.

### Device-Level Properties Overview

| Property Path | Type | Access | Description |
|---------------|------|--------|-------------|
| `buttonInputDescriptions` | array | r | Descriptions of button inputs (invariable) |
| `buttonInputSettings` | array | r/w | Settings for button inputs (persistent) |
| `buttonInputStates` | array | r | Current state of button inputs |
| `binaryInputDescriptions` | array | r | Descriptions of binary inputs (invariable) |
| `binaryInputSettings` | array | r/w | Settings for binary inputs (persistent) |
| `binaryInputStates` | array | r | Current state of binary inputs |
| `sensorDescriptions` | array | r | Descriptions of sensors (invariable) |
| `sensorSettings` | array | r/w | Settings for sensors (persistent) |
| `sensorStates` | array | r | Current sensor readings |
| `outputDescription` | object | r | Output description (invariable) |
| `outputSettings` | object | r/w | Output settings (persistent) |
| `outputState` | object | r | Current output state |
| `channelDescriptions` | array | r | Channel descriptions (invariable) |
| `channelSettings` | array | r/w | Channel settings (persistent) |
| `channelStates` | array | r | Current channel states |
| `scenes` | array | r/w | Scene configurations |
| `deviceActionDescriptions` | array | r | Available action templates |
| `standardActions` | array | r | Predefined standard actions |
| `customActions` | array | r/w | User-configured custom actions |
| `dynamicDeviceActions` | array | r | Device-created dynamic actions |
| `deviceStateDescriptions` | array | r | Device state descriptions |
| `deviceStates` | array | r | Current device state values |
| `devicePropertyDescriptions` | array | r | Custom property descriptions |
| `deviceProperties` | array | r/w | Custom property values |
| `deviceEventDescriptions` | array | r | Device event descriptions |
| `controlValues` | object | r/w | Named control values |

### Button Input Properties

Button inputs represent physical buttons or switches on devices.

#### Button Input Description

Invariable properties describing button capabilities. Located in `buttonInputDescriptions[i]`:

| Property | Type | Access | Description |
|----------|------|--------|-------------|
| `buttonID` | integer | r | Numeric ID of the button |
| `buttonType` | integer | r | Button type: 0=undefined, 1=single push, 2=two-way directional, 3=4-way directional, 4=8-position mode selector |
| `supportsLocalKeyMode` | boolean | r | Whether button supports local key mode |
| `buttonElementID` | integer | r | Element ID within button (0..N-1) |
| `buttonFunc` | integer | r | Function: 0=inactive/room off, 1=area 1 on, 2=area 2 on, 3=area 3 on, 4=area 4 on, 5=reserved, 6=area 1 preset 0, 7=area 1 preset 1, etc. |

#### Button Input Settings

Persistent configuration for buttons. Located in `buttonInputSettings[i]`:

| Property | Type | Access | Description |
|----------|------|--------|-------------|
| `group` | integer | r/w | dS group number this button controls |
| `mode` | integer | r/w | Button mode: 0=inactive, 1=standard, 2=turbo, 3=special mode, 127=default |
| `channel` | integer | r/w | Channel number for advanced button features |
| `setsLocalPriority` | boolean | r/w | Whether button press sets local priority |
| `callsPresent` | boolean | r/w | Whether button calls "present" scene |
| `buttonActionMode` | integer | r/w | Action mode: 0=no action, 1=standard, 2=pulse |
| `buttonActionId` | string | r/w | ID of action to execute on button press |

#### Button Input State

Current button state. Located in `buttonInputStates[i]`:

| Property | Type | Access | Description |
|----------|------|--------|-------------|
| `value` | double | r | Current button state value |
| `age` | double | r | Age of value in seconds |
| `localPriority` | boolean | r | Whether local priority is active |
| `callScene` | integer | r | Last scene number called by button |

### Binary Input Properties

Binary inputs represent simple on/off inputs like door contacts or motion sensors.

#### Binary Input Description

Invariable properties. Located in `binaryInputDescriptions[i]`:

| Property | Type | Access | Description |
|----------|------|--------|-------------|
| `inputType` | integer | r | Type: 0=none, 1=presence detector, 2=light detector, 3=presence in darkness, 4=twilight, 5=motion, 6=motion in darkness, 7=smoke, 8=wind strength, 9=rain, 10=sun radiation, 11=thermostat, 12=lowBattery, 13=window handle, 14=door contact, 15=window contact, 16=motion detector, 17=freeze detector, 18=electric usage monitor, 19=key, 20=device button, 21=reserved |
| `inputUsage` | integer | r | Usage: 0=undefined, 1=room, 2=outdoor, 3=user interaction |
| `hardwareName` | string | r | Hardware connector name/label |

#### Binary Input Settings

Persistent configuration. Located in `binaryInputSettings[i]`:

| Property | Type | Access | Description |
|----------|------|--------|-------------|
| `group` | integer | r/w | dS group number |
| `minPushInterval` | double | r/w | Minimum interval between state pushes (seconds, default=0.1) |
| `changesOnlyInterval` | double | r/w | Minimum interval for identical value pushes (default=0) |
| `aliveSignInterval` | double | r/w | Maximum interval between updates before considered offline |

#### Binary Input State

Current state. Located in `binaryInputStates[i]`:

| Property | Type | Access | Description |
|----------|------|--------|-------------|
| `value` | double or NULL | r | Current binary state (usually 0 or 1) |
| `age` | double or NULL | r | Age of state in seconds |
| `error` | integer | r | Error code: 0=ok, 1=open circuit, 2=short circuit, 4=bus problem, 5=low battery, 6=other error |

### Sensor Properties

Sensors provide analog measurements like temperature, humidity, etc.

#### Sensor Description

Invariable sensor properties. Located in `sensorDescriptions[i]`:

| Property | Type | Access | Description |
|----------|------|--------|-------------|
| `sensorType` | integer | r | Sensor type (see Sensor Types table below) |
| `sensorUsage` | integer | r | Usage: 0=undefined, 1=room, 2=outdoor, 3=user interaction, 4=device total, 5=device last run, 6=device average |
| `min` | double | r | Minimum sensor value |
| `max` | double | r | Maximum sensor value |
| `resolution` | double | r | Resolution (LSB size of hardware sensor) |
| `updateInterval` | double | r | How fast value is tracked (seconds) |
| `aliveSignInterval` | double | r | Maximum interval before considered offline |

**Sensor Types:**

| Type | Description | Unit |
|------|-------------|------|
| 0 | Temperature | °C |
| 1 | Relative humidity | % |
| 2 | Brightness | lux |
| 3 | Precipitation intensity | mm/h |
| 4 | Wind speed | m/s |
| 5 | Air pressure | hPa |
| 6 | Wind gust speed | m/s |
| 7 | Gas concentration (CO, methane) | ppm |
| 8 | Particles <10µm | µg/m³ |
| 9 | Particles <2.5µm | µg/m³ |
| 10 | Particles <1µm | µg/m³ |
| 11 | Room operating panel set point | % (0-100) |
| 12 | Fan speed | 0-1 (0=off, <0=auto) |
| 13 | Wind speed (average) | m/s |
| 14 | Active power | W |
| 15 | Electric current | A |
| 16 | Energy meter | kWh |
| 17 | Apparent power | VA |
| 18 | Air pressure | hPa |
| 19 | Wind direction | degrees |
| 20 | Sound pressure level | dB |
| 21 | Precipitation (hourly sum) | mm/m² |
| 22 | CO₂ concentration | ppm |
| 23 | Wind gust speed | m/s |
| 24 | Wind gust direction | degrees |
| 25 | Generated active power | W |
| 26 | Generated energy | kWh |
| 27 | Water quantity | L |
| 28 | Water flow rate | L/s |

#### Sensor Settings

Persistent configuration. Located in `sensorSettings[i]`:

| Property | Type | Access | Description |
|----------|------|--------|-------------|
| `group` | integer | r/w | dS group number |
| `minPushInterval` | double | r/w | Minimum interval between pushes (seconds, default=2) |
| `changesOnlyInterval` | double | r/w | Minimum interval for same-value pushes (default=0) |

#### Sensor State

Current readings. Located in `sensorStates[i]`:

| Property | Type | Access | Description |
|----------|------|--------|-------------|
| `value` | double or NULL | r | Current sensor value (NULL if no recent reading) |
| `age` | double or NULL | r | Age of reading in seconds (NULL if no data) |
| `contextId` | integer or NULL | r | Numerical context data ID (optional) |
| `contextMsg` | string or NULL | r | Text context message (optional) |
| `error` | integer | r | Error code: 0=ok, 1=open circuit, 2=short circuit, 4=bus problem, 5=low battery, 6=other error |

### Output Properties

Output properties describe device output capabilities (lights, blinds, valves, etc.). Devices without output functionality return NULL for these properties.

#### Output Description

Invariable output properties. Located in `outputDescription`:

| Property | Type | Access | Description |
|----------|------|--------|-------------|
| `defaultGroup` | integer | r | Default dS Application ID |
| `name` | string | r | Human-readable output name/label |
| `function` | integer | r | Output function type (see Output Functions table below) |
| `outputUsage` | integer | r | Usage: 0=undefined, 1=room, 2=outdoors, 3=user display/indicator |
| `variableRamp` | boolean | r | Whether output supports variable transition times |
| `maxPower` | double | r (opt) | Maximum output power in Watts |
| `activeCoolingMode` | boolean | r (opt) | True if device can actively cool (e.g., air conditioning) |

**Output Functions:**

| Value | Description | Channels |
|-------|-------------|----------|
| 0 | On/off only | Channel 1 ("brightness"), switched on when >onThreshold |
| 1 | Dimmer | Channel 1 ("brightness") |
| 2 | Positional (blinds, valves) | Positional control |
| 3 | Dimmer with color temperature | Channels 1 & 4 ("brightness", "ct") |
| 4 | Full color dimmer | Channels 1-6 ("brightness", "hue", "saturation", "ct", "cieX", "cieY") |
| 5 | Bipolar (heating/cooling) | Negative and positive values |
| 6 | Internally controlled | Device has integrated control algorithm |

#### Output Settings

Persistent output configuration. Located in `outputSettings`:

| Property | Type | Access | Description |
|----------|------|--------|-------------|
| `activeGroup` | integer | r/w | Active dS Application ID |
| `groups` | object | r/w | Group memberships (property elements named "1"-"63", value=boolean) |
| `mode` | integer | r/w | Mode: 0=disabled, 1=binary, 2=gradual, 127=default |
| `pushChanges` | boolean | r/w | Whether local changes are pushed to vdSM |
| `onThreshold` | double | r/w (opt) | Minimum brightness to switch on (%, default=50) |
| `minBrightness` | double | r/w (opt) | Minimum hardware brightness for dimming (%) |
| `dimTimeUp` | integer | r/w (opt) | Dim up time (8-bit dS format) |
| `dimTimeDown` | integer | r/w (opt) | Dim down time (8-bit dS format) |
| `dimTimeUpAlt1` | integer | r/w (opt) | Alternate 1 dim up time |
| `dimTimeDownAlt1` | integer | r/w (opt) | Alternate 1 dim down time |
| `dimTimeUpAlt2` | integer | r/w (opt) | Alternate 2 dim up time |
| `dimTimeDownAlt2` | integer | r/w (opt) | Alternate 2 dim down time |
| `heatingSystemCapability` | integer | r/w (opt) | Climate control capability: 1=heating only, 2=cooling only, 3=both |
| `heatingSystemType` | integer | r/w (opt) | Valve/actuator type: 0=undefined, 1=floor heating, 2=radiator, 3=wall heating, 4=convector passive, 5=convector active, 6=floor heating low energy |

**Note:** Dim time format: `4 MSB = exp, 4 LSB = lin, time = 100ms/32 × 2^exp × (17 + lin)`

#### Output State

Current output state. Located in `outputState`:

| Property | Type | Access | Description |
|----------|------|--------|-------------|
| `localPriority` | boolean | r/w | Whether local priority is enabled (device ignores scene calls unless forced) |
| `error` | integer | r | Error code: 0=ok, 1=open circuit/lamp broken, 2=short circuit, 3=overload, 4=bus problem, 5=low battery, 6=other error |

### Channel Properties

Channels represent individual controllable aspects of outputs (brightness, hue, saturation, position, etc.).

#### Channel Description

Invariable channel properties. Located in `channelDescriptions[i]`:

| Property | Type | Access | Description |
|----------|------|--------|-------------|
| `name` | string | r | Human-readable channel name/label |
| `channelType` | integer | r | Numerical channel type ID (see ds-basics.pdf for definitions) |
| `dsIndex` | integer | r | Channel index 0..N-1 for dS-OS/DSMAPI addressing (index 0 = default output) |
| `min` | double | r | Minimum channel value |
| `max` | double | r | Maximum channel value |
| `resolution` | double | r | Channel resolution |

**Common Channel Types:**
- 0: Default/generic channel
- 1: Brightness (0-100%)
- 2: Hue (0-360°)
- 3: Saturation (0-100%)
- 4: Color temperature (CT)
- 5: CIE X coordinate
- 6: CIE Y coordinate

#### Channel Settings

Currently no per-channel settings are defined. Located in `channelSettings[i]`:

| Property | Type | Access | Description |
|----------|------|--------|-------------|
| - | - | - | No properties currently defined |

#### Channel State

Current channel values. Located in `channelStates[i]`:

**Important:** Channel state must not be written directly. Use `VDSM_NOTIFICATION_SET_OUTPUT_CHANNEL_VALUE` instead.

| Property | Type | Access | Description |
|----------|------|--------|-------------|
| `value` | double | r | Current channel value (brightness, position, etc.) |
| `age` | double | r | Age of value in seconds since last hardware update (NULL if value set but not yet applied) |

### Scene Properties

Scenes store sets of values to apply to device outputs. Each scene contains values organized both by output number and by channel type. Located in `scenes[i]`:

| Property | Type | Access | Description |
|----------|------|--------|-------------|
| `channels` | object | r/w | Scene values per channel type (property elements named by channel type ID) |
| `effect` | integer | r/w | Scene effect: 0=immediate, 1=smooth normal, 2=slow, 3=very slow, 4=blink/alert |
| `dontCare` | boolean | r/w | Global don't-care flag (if set, no channel values are applied) |
| `ignoreLocalPriority` | boolean | r/w | Whether this scene overrides local priority |

#### Scene Value

Each scene channel value contains. Located in `scenes[i].channels[channelTypeId]`:

| Property | Type | Access | Description |
|----------|------|--------|-------------|
| `value` | double | r/w | Value to apply (same range as channel value) |
| `dontCare` | boolean | r/w | Channel-specific don't-care (if set, this channel value is not applied) |
| `automatic` | boolean | r/w | Channel-specific automatic flag |

**Scene Effect Behavior:**
- Scene values may or may not be used depending on effect type
- Blink effect uses color values regardless of dontCare flags
- When effect finishes, channels with dontCare=true revert to pre-effect values
- Channels with dontCare=false have scene values applied

### Device Actions

Actions describe device functionalities and operation processes.

#### Device Action Descriptions

Templates for creating custom actions. Located in `deviceActionDescriptions[i]`:

| Property | Type | Access | Description |
|----------|------|--------|-------------|
| `name` | string | r | Action template name |
| `params` | array | r | Parameter objects describing action parameters |
| `description` | string | r (opt) | Human-readable action description |

**Parameter Object Structure:**

| Property | Type | Description |
|----------|------|-------------|
| `type` | string | Data type: "numeric", "enumeration", or "string" |
| `min` | double | Minimum value (numeric only) |
| `max` | double | Maximum value (numeric only) |
| `resolution` | double | Value resolution (numeric only) |
| `siunit` | string | SI unit string (e.g., "kW", "mA") |
| `options` | object | Key-value pairs for enumeration choices |
| `default` | varies | Default parameter value |

#### Standard Actions

Predefined immutable actions. Located in `standardActions[i]`:

| Property | Type | Access | Description |
|----------|------|--------|-------------|
| `name` | string | r | Unique action ID (always has "std." prefix) |
| `action` | string | r | Template action name this is based on |
| `params` | object | r (opt) | Parameter name-value pairs differing from template |

#### Custom Actions

User-configured actions. Located in `customActions[i]`:

| Property | Type | Access | Description |
|----------|------|--------|-------------|
| `name` | string | r/w | Unique action ID (always has "custom." prefix) |
| `action` | string | r/w | Template action name this is based on |
| `title` | string | r/w | Human-readable action name (usually user-provided) |
| `params` | object | r/w (opt) | Parameter name-value pairs differing from template |

#### Dynamic Device Actions

Device-created actions. Located in `dynamicDeviceActions[i]`:

| Property | Type | Access | Description |
|----------|------|--------|-------------|
| `name` | string | r | Unique action ID (always has "dynamic." prefix) |
| `title` | string | r | Human-readable action name |

### Device States and Properties

Device states and properties provide generic extensibility for device-specific data.

#### Device State Descriptions

State type definitions. Located in `deviceStateDescriptions[i]`:

| Property | Type | Access | Description |
|----------|------|--------|-------------|
| `name` | string | r | State name |
| `options` | object | r | Option ID-value pairs (e.g., 0=Off, 1=Initializing, 2=Running, 3=Shutdown) |
| `description` | string | r (opt) | State description |

#### Device State Values

Current state values. Located in `deviceStates[i]`:

| Property | Type | Access | Description |
|----------|------|--------|-------------|
| `name` | string | r | State name |
| `value` | string | r | Current state option value |

**Note:** State changes are signaled with push notifications containing the new state value.

#### Device Property Descriptions

Custom property type definitions. Located in `devicePropertyDescriptions[i]`:

| Property | Type | Access | Description |
|----------|------|--------|-------------|
| `name` | string | r | Property name |
| `type` | string | r | Data type: "numeric", "enumeration", or "string" |
| `min` | double | r (opt) | Minimum value (numeric only) |
| `max` | double | r (opt) | Maximum value (numeric only) |
| `resolution` | double | r (opt) | Resolution (numeric only) |
| `siunit` | string | r (opt) | SI unit string |
| `options` | object | r (opt) | Option ID-value pairs (enumeration only) |
| `default` | varies | r (opt) | Default property value |

#### Device Property Values

Custom property values. Located in `deviceProperties[i]`:

| Property | Type | Access | Description |
|----------|------|--------|-------------|
| `name` | string | r | Property name |
| `value` | string | r/w | Current property value |

### Device Events

Stateless device events. Located in `deviceEventDescriptions[i]`:

| Property | Type | Access | Description |
|----------|------|--------|-------------|
| `name` | string | r | Event name |
| `description` | string | r (opt) | Event description |

### Control Values

Named control values for device operation. Located in `controlValues`:

Control values provide a generic mechanism for controlling device behavior through named parameters. The specific control values available depend on device type and capabilities.

**Example Control Values:**
- `heatingLevel`: Climate control heating/cooling level (-100 to 100)
- `temperature`: Target temperature setpoint
- Custom device-specific controls

Each control value is accessed as a named property within the `controlValues` object and typically has a double value type.

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

- **[Protocol Buffers Reference](06-protobuf-reference.md)** - Using properties in messages
- **[Protocol Buffers](06-protobuf-reference.md)** - PropertyElement structure
- **[Quick Start Guide](02-quickstart.md)** - Implementing device properties

---

**Related:**
- [Core Concepts](03-core-concepts.md) - Understanding device model
- [Error Handling](08-error-handling.md) - Property access errors
