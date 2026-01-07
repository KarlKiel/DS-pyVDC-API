# DS-pyVDC-API - Complete API Reference

This document provides a comprehensive reference for all classes, methods, and functions in the DS-pyVDC-API library.

## Table of Contents

1. [VdcHost](#vdchost)
2. [VdcDevice](#vdcdevice)
3. [MessageHandler](#messagehandler)
4. [Property Utilities](#property-utilities)
5. [Protocol Buffer Messages](#protocol-buffer-messages)

---

## VdcHost

Main class for implementing a vDC host server that manages virtual devices and communicates with vdSM.

### Constructor

```python
VdcHost(dsuid: str, vdc_dsuid: str, port: int = 8444)
```

**Parameters:**
- `dsuid` (str): 34-character hexadecimal dSUID for the vDC host
- `vdc_dsuid` (str): 34-character hexadecimal dSUID for the vDC itself
- `port` (int, optional): TCP port to listen on. Default: 8444

**Raises:**
- `ValueError`: If dSUID is not exactly 34 characters

**Example:**
```python
host = VdcHost(
    dsuid="AA000000000000000000000000000000AA",
    vdc_dsuid="BB000000000000000000000000000000BB",
    port=8444
)
```

### Properties

- `dsuid` (str): The vDC host's dSUID
- `vdc_dsuid` (str): The vDC's dSUID
- `port` (int): TCP port the server listens on
- `api_version` (int): Supported API version (3)
- `devices` (Dict[str, VdcDevice]): Dictionary of registered devices (keyed by dSUID)
- `session_active` (bool): Whether a vdSM session is currently active
- `vdsm_dsuid` (Optional[str]): dSUID of connected vdSM (if session active)

### Methods

#### add_device

```python
add_device(device: VdcDevice) -> None
```

Add a virtual device to this vDC host. If a session is active, the device is immediately announced to vdSM.

**Parameters:**
- `device` (VdcDevice): Device instance to add

**Example:**
```python
light = VdcDevice(dsuid="...", name="Living Room")
host.add_device(light)
```

#### remove_device

```python
remove_device(dsuid: str) -> None
```

Remove a virtual device from this vDC host. If a session is active, sends a vanish message to vdSM.

**Parameters:**
- `dsuid` (str): dSUID of device to remove

#### start

```python
start(blocking: bool = True) -> None
```

Start the vDC host server.

**Parameters:**
- `blocking` (bool, optional): If True, blocks until server stops. If False, runs in background thread. Default: True

**Example:**
```python
# Blocking mode (typical usage)
host.start()

# Non-blocking mode
host.start(blocking=False)
# ... do other work ...
host.stop()
```

#### stop

```python
stop() -> None
```

Stop the vDC host server and close all connections.

---

## VdcDevice

Represents a virtual device in the vDC system.

### Constructor

```python
VdcDevice(dsuid: str, name: str, model: str = "Generic Device",
          model_uid: str = "vdc:generic", device_class: str = "Light")
```

**Parameters:**
- `dsuid` (str): 34-character hexadecimal dSUID
- `name` (str): Human-readable device name
- `model` (str, optional): Model name. Default: "Generic Device"
- `model_uid` (str, optional): Unique model identifier. Default: "vdc:generic"
- `device_class` (str, optional): Device class. Default: "Light"

**Valid device classes:**
- `Light`, `Shade`, `Heating`, `Cooling`, `Ventilation`
- `Window`, `Joker`, `Audio`, `Video`, `SecuritySystem`
- `Access`, `SingleButton`

**Raises:**
- `ValueError`: If dSUID is not exactly 34 characters

**Example:**
```python
device = VdcDevice(
    dsuid="CC000000000000000000000000000000C1",
    name="Bedroom Light",
    model="Smart Bulb Pro",
    model_uid="com.example.smartbulb.v2",
    device_class="Light"
)
```

### Properties

- `dsuid` (str): Device's dSUID
- `name` (str): Device name
- `model` (str): Model name
- `model_uid` (str): Model unique identifier
- `device_class` (str): Device class
- `vdc_dsuid` (Optional[str]): Parent vDC's dSUID (set by VdcHost)
- `output_value` (float): Current output value (0.0-100.0)
- `output_mode` (int): Current output mode

### Methods to Override

These methods can be overridden in subclasses for custom behavior:

#### call_scene

```python
call_scene(scene: int, force: bool = False) -> None
```

Called when a scene is called on this device.

**Parameters:**
- `scene` (int): Scene number (0-126)
- `force` (bool): Force execution even if device has local priority

**Default behavior:** Maps common scene numbers to output values (0=off, 5=100%, etc.)

**Example:**
```python
class MyLight(VdcDevice):
    def call_scene(self, scene: int, force: bool = False):
        super().call_scene(scene, force)
        print(f"Scene {scene} called, output now {self.output_value}%")
```

#### set_output_value

```python
set_output_value(value: float, apply_now: bool = True) -> None
```

Set the output channel value.

**Parameters:**
- `value` (float): Output value (typically 0.0-100.0)
- `apply_now` (bool): Apply immediately or stage for later

#### dim_channel

```python
dim_channel(mode: int, channel: int = 0) -> None
```

Start/stop dimming a channel.

**Parameters:**
- `mode` (int): Dim mode (0=stop, 1=up, -1=down)
- `channel` (int, optional): Channel number. Default: 0

#### identify

```python
identify() -> None
```

Identify the device (e.g., blink, beep). Override to implement actual behavior.

### Property Methods

#### get_basic_properties

```python
get_basic_properties() -> Dict[str, Any]
```

Get the basic common properties for this device.

**Returns:**
Dict with keys: dSUID, name, model, modelUID, type, deviceClass

#### get_property_tree

```python
get_property_tree(query: Optional[List[PropertyElement]] = None) -> List[PropertyElement]
```

Get property tree for this device, optionally filtered by query.

**Parameters:**
- `query` (Optional): List of PropertyElement objects specifying which properties to return

**Returns:**
List of PropertyElement protobuf objects

#### set_property

```python
set_property(name: str, value: Any) -> None
```

Set a property value on this device.

**Parameters:**
- `name` (str): Property name
- `value` (Any): New property value

---

## MessageHandler

Low-level Protocol Buffer message framing and I/O.

### Class Methods

#### receive_message

```python
@staticmethod
receive_message(sock: socket.socket) -> Optional[Message]
```

Receive a protobuf message from a socket.

**Parameters:**
- `sock` (socket.socket): Socket to receive from

**Returns:**
- Parsed Message object, or None if connection closed

**Raises:**
- `ValueError`: If message size exceeds maximum (16384 bytes)

#### send_message

```python
@staticmethod
send_message(sock: socket.socket, msg: Message) -> None
```

Send a protobuf message to a socket.

**Parameters:**
- `sock` (socket.socket): Socket to send to
- `msg` (Message): Message to send

**Raises:**
- `ValueError`: If message size exceeds maximum (16384 bytes)

---

## Property Utilities

### PropertyValue

Helper class for creating and converting PropertyValue objects.

#### from_python

```python
@staticmethod
from_python(value: Any) -> PropertyValue
```

Convert a Python value to a PropertyValue protobuf object.

**Parameters:**
- `value` (Any): Python value (bool, int, float, str, bytes)

**Returns:**
PropertyValue protobuf object

**Example:**
```python
pv = PropertyValue.from_python("Hello")  # Creates v_string
pv = PropertyValue.from_python(42)       # Creates v_uint64 or v_int64
pv = PropertyValue.from_python(3.14)     # Creates v_double
pv = PropertyValue.from_python(True)     # Creates v_bool
```

#### to_python

```python
@staticmethod
to_python(pv: PropertyValue) -> Any
```

Convert a PropertyValue protobuf object to a Python value.

**Parameters:**
- `pv` (PropertyValue): PropertyValue protobuf object

**Returns:**
Python value (bool, int, float, str, bytes, or None)

### PropertyElement

Helper class for building PropertyElement trees.

#### create

```python
@staticmethod
create(name: str, value: Any = None, elements: List[PropertyElement] = None) -> PropertyElement
```

Create a PropertyElement with the given name, value, and/or child elements.

**Parameters:**
- `name` (str): Property name
- `value` (Any, optional): Value (converted to PropertyValue)
- `elements` (List[PropertyElement], optional): Child elements

**Returns:**
PropertyElement protobuf object

### build_property_tree

```python
build_property_tree(data: Dict[str, Any]) -> List[PropertyElement]
```

Build a property tree from a nested dictionary structure.

**Parameters:**
- `data` (Dict): Dictionary representing the property tree

**Returns:**
List of PropertyElement objects

**Example:**
```python
tree = build_property_tree({
    "dSUID": "123...",
    "name": "My Device",
    "output": {
        "value": 75.0,
        "mode": 1
    }
})
```

### property_tree_to_dict

```python
property_tree_to_dict(elements: List[PropertyElement]) -> Dict[str, Any]
```

Convert a property tree to a nested dictionary.

**Parameters:**
- `elements` (List[PropertyElement]): List of PropertyElement objects

**Returns:**
Dictionary representation of the property tree

---

## Protocol Buffer Messages

The library uses auto-generated classes from `genericVDC.proto`. Key message types:

### Message

Container for all vDC messages.

**Fields:**
- `type` (Type enum): Message type
- `message_id` (uint32): Unique ID for request/response matching
- `generic_response` (GenericResponse): Error response
- Various message-specific fields (100-123)

### Type Enum

Message type identifiers:

**Session Management:**
- `VDSM_REQUEST_HELLO` (2)
- `VDC_RESPONSE_HELLO` (3)
- `VDSM_SEND_PING` (8)
- `VDC_SEND_PONG` (9)
- `VDSM_SEND_BYE` (14)

**Device Lifecycle:**
- `VDC_SEND_ANNOUNCE_VDC` (23)
- `VDC_SEND_ANNOUNCE_DEVICE` (10)
- `VDC_SEND_VANISH` (11)

**Properties:**
- `VDSM_REQUEST_GET_PROPERTY` (4)
- `VDC_RESPONSE_GET_PROPERTY` (5)
- `VDSM_REQUEST_SET_PROPERTY` (6)

**Notifications:**
- `VDSM_NOTIFICATION_CALL_SCENE` (15)
- `VDSM_NOTIFICATION_SAVE_SCENE` (16)
- `VDSM_NOTIFICATION_SET_OUTPUT_CHANNEL_VALUE` (25)
- `VDSM_NOTIFICATION_DIM_CHANNEL` (24)
- `VDSM_NOTIFICATION_IDENTIFY` (20)

### ResultCode Enum

Error codes in GenericResponse:

- `ERR_OK` (0): Success
- `ERR_MESSAGE_UNKNOWN` (1): Unknown message type
- `ERR_INCOMPATIBLE_API` (2): API version mismatch
- `ERR_SERVICE_NOT_AVAILABLE` (3): Service unavailable
- `ERR_FORBIDDEN` (5): Operation forbidden
- `ERR_NOT_IMPLEMENTED` (6): Feature not implemented
- `ERR_INVALID_VALUE_TYPE` (8): Invalid value type
- `ERR_MISSING_DATA` (10): Required data missing
- `ERR_NOT_FOUND` (11): Resource not found
- `ERR_NOT_AUTHORIZED` (12): Not authorized

---

## Error Handling

All methods that can fail will raise appropriate Python exceptions:

- `ValueError`: Invalid parameter values (wrong dSUID length, message too large, etc.)
- `socket.error`: Network/connection errors
- `Exception`: General errors (logged with details)

Example:
```python
try:
    host = VdcHost(dsuid="INVALID", vdc_dsuid="...", port=8444)
except ValueError as e:
    print(f"Invalid dSUID: {e}")
```

---

## Logging

The library uses Python's `logging` module. Configure in your application:

```python
import logging

# Basic configuration
logging.basicConfig(level=logging.INFO)

# Or configure specific logger
logger = logging.getLogger('ds_vdc_api')
logger.setLevel(logging.DEBUG)
```

Logger names:
- `ds_vdc_api.vdc_host`: VdcHost logging
- `ds_vdc_api.vdc_device`: VdcDevice logging
- `ds_vdc_api.message_handler`: MessageHandler logging

---

## Complete Example

```python
import logging
from ds_vdc_api import VdcHost, VdcDevice

# Configure logging
logging.basicConfig(level=logging.INFO)

# Create custom device class
class SmartBulb(VdcDevice):
    def call_scene(self, scene: int, force: bool = False):
        super().call_scene(scene, force)
        print(f"Bulb '{self.name}': Scene {scene} -> {self.output_value}%")
    
    def identify(self):
        print(f"Bulb '{self.name}': Blinking for identification!")

# Create host
host = VdcHost(
    dsuid="AA000000000000000000000000000000AA",
    vdc_dsuid="BB000000000000000000000000000000BB",
    port=8444
)

# Create and add devices
bulb1 = SmartBulb(
    dsuid="CC000000000000000000000000000000C1",
    name="Living Room",
    model="Smart Bulb Pro"
)
host.add_device(bulb1)

bulb2 = SmartBulb(
    dsuid="CC000000000000000000000000000000C2",
    name="Bedroom",
    model="Smart Bulb Pro"
)
host.add_device(bulb2)

# Start server
print(f"Starting vDC host with {len(host.devices)} devices...")
try:
    host.start()  # Blocks until Ctrl+C
except KeyboardInterrupt:
    print("Shutting down...")
    host.stop()
```
