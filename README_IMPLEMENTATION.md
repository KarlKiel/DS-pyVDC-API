# DS-pyVDC-API Implementation

This is a Python implementation of the digitalSTROM Virtual Device Connector (vDC) API. It provides a complete, easy-to-use library for creating vDC integrations with the digitalSTROM home automation system.

## Features

- ✅ **Complete Protocol Implementation**: Full support for vDC API v3
- ✅ **Protocol Buffers**: Auto-generated from `genericVDC.proto`
- ✅ **Session Management**: Automatic hello handshake, ping/pong
- ✅ **Device Management**: Easy device announcement and lifecycle
- ✅ **Property System**: Type-safe property tree building and querying
- ✅ **Scene Support**: Scene calling, saving, undo
- ✅ **Channel Control**: Output values, dimming
- ✅ **Extensible**: Easy to subclass for custom device types
- ✅ **Well Documented**: Comprehensive docs and examples

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/KarlKiel/DS-pyVDC-API.git
cd DS-pyVDC-API

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Requirements

- Python 3.7+
- protobuf >= 3.20.0

## Quick Start

Here's a minimal example to get started:

```python
from ds_vdc_api import VdcHost, VdcDevice

# Create a vDC host
host = VdcHost(
    dsuid="AA000000000000000000000000000000AA",  # 34-char hex dSUID
    vdc_dsuid="BB000000000000000000000000000000BB",
    port=8444
)

# Create a virtual light device
light = VdcDevice(
    dsuid="CC000000000000000000000000000000C1",
    name="Living Room Light",
    model="Virtual Light",
    device_class="Light"
)

# Add device and start
host.add_device(light)
host.start()  # Blocks until Ctrl+C
```

## Architecture

The library is organized into several key modules:

### Core Modules

- **`vdc_host.py`**: Main VdcHost class - manages TCP server, sessions, and message routing
- **`vdc_device.py`**: VdcDevice class - represents virtual devices with properties and state
- **`message_handler.py`**: Low-level Protocol Buffer message framing and I/O
- **`property_tree.py`**: Utilities for building and manipulating property trees
- **`genericVDC_pb2.py`**: Auto-generated Protocol Buffer classes

### Class Overview

```
VdcHost
├── Manages TCP server (default port 8444)
├── Handles session initialization (hello handshake)
├── Routes messages to appropriate handlers
├── Manages device announcements
└── Maintains device registry

VdcDevice
├── Represents a virtual device
├── Stores device properties (dSUID, name, model, etc.)
├── Maintains device state (output values, scenes)
├── Handles scene calls, dimming, identify
└── Extensible via subclassing

MessageHandler
├── Sends/receives Protocol Buffer messages
├── Handles 2-byte length framing
└── Network byte order conversion

PropertyElement/PropertyValue
├── Type-safe property value handling
├── Tree structure building
└── Python ↔ Protocol Buffer conversion
```

## Usage Examples

### Example 1: Simple vDC Host

See `examples/simple_vdc_host.py` for a complete example with multiple devices.

```bash
python examples/simple_vdc_host.py
```

### Example 2: Custom Device Classes

Create custom device types by subclassing `VdcDevice`:

```python
from ds_vdc_api import VdcDevice

class SmartBulb(VdcDevice):
    def __init__(self, dsuid: str, name: str):
        super().__init__(
            dsuid=dsuid,
            name=name,
            model="Smart Bulb Pro",
            device_class="Light"
        )
        self.color_temperature = 2700  # Kelvin
    
    def call_scene(self, scene: int, force: bool = False):
        super().call_scene(scene, force)
        print(f"Bulb {self.name}: Scene {scene} called")
    
    def identify(self):
        print(f"Bulb {self.name}: Flashing for identification!")
```

See `examples/custom_devices.py` for more details.

### Example 3: Property Handling

```python
from ds_vdc_api.property_tree import build_property_tree

# Build a property tree from a dictionary
properties = build_property_tree({
    "dSUID": "123456789ABCDEF...",
    "name": "My Device",
    "output": {
        "value": 75.0,
        "mode": 1
    }
})

# Properties are now ready to send in a VDC_RESPONSE_GET_PROPERTY message
```

## API Reference

### VdcHost

```python
class VdcHost:
    def __init__(self, dsuid: str, vdc_dsuid: str, port: int = 8444)
    def add_device(self, device: VdcDevice) -> None
    def remove_device(self, dsuid: str) -> None
    def start(self, blocking: bool = True) -> None
    def stop(self) -> None
```

### VdcDevice

```python
class VdcDevice:
    def __init__(self, dsuid: str, name: str, model: str = "Generic Device",
                 model_uid: str = "vdc:generic", device_class: str = "Light")
    
    # Methods to override in custom devices
    def call_scene(self, scene: int, force: bool = False) -> None
    def set_output_value(self, value: float, apply_now: bool = True) -> None
    def dim_channel(self, mode: int, channel: int = 0) -> None
    def identify(self) -> None
    
    # Property handling
    def get_basic_properties(self) -> Dict[str, Any]
    def get_property_tree(self, query: Optional[List[PropertyElement]] = None)
    def set_property(self, name: str, value: Any) -> None
```

### Message Types Supported

The implementation supports all major vDC API message types:

**Session Management:**
- `VDSM_REQUEST_HELLO` / `VDC_RESPONSE_HELLO`
- `VDSM_SEND_PING` / `VDC_SEND_PONG`
- `VDSM_SEND_BYE`

**Device Lifecycle:**
- `VDC_SEND_ANNOUNCE_VDC`
- `VDC_SEND_ANNOUNCE_DEVICE`
- `VDC_SEND_VANISH`

**Properties:**
- `VDSM_REQUEST_GET_PROPERTY` / `VDC_RESPONSE_GET_PROPERTY`
- `VDSM_REQUEST_SET_PROPERTY`

**Notifications:**
- `VDSM_NOTIFICATION_CALL_SCENE`
- `VDSM_NOTIFICATION_SAVE_SCENE`
- `VDSM_NOTIFICATION_UNDO_SCENE`
- `VDSM_NOTIFICATION_SET_OUTPUT_CHANNEL_VALUE`
- `VDSM_NOTIFICATION_DIM_CHANNEL`
- `VDSM_NOTIFICATION_IDENTIFY`
- `VDSM_NOTIFICATION_SET_CONTROL_VALUE`

## Device Classes

Supported device classes (as per digitalSTROM specification):

- `Light` - Lighting devices
- `Shade` - Blinds and shades
- `Heating` - Heating devices
- `Cooling` - Cooling/AC devices
- `Ventilation` - Ventilation systems
- `Window` - Window controls
- `Joker` - Multi-purpose devices
- `Audio` - Audio systems
- `Video` - Video systems
- `SecuritySystem` - Security devices
- `Access` - Access control
- `SingleButton` - Button devices

## Protocol Details

### Message Framing

All Protocol Buffer messages are sent over TCP with a 2-byte length header:

```
┌─────────────┬────────────────────┐
│ Length (2B) │  Protobuf Message  │
│ (uint16_t)  │   (variable size)  │
│ Big-endian  │                    │
└─────────────┴────────────────────┘
```

Maximum message size: 16 KB (16384 bytes)

### Session Flow

```
vdSM                           vDC Host
  │                                │
  ├─── TCP Connect ───────────────►│
  │                                │
  ├─── VDSM_REQUEST_HELLO ────────►│
  │    (api_version, dSUID)        │
  │                                │
  │◄─── VDC_RESPONSE_HELLO ────────┤
  │    (dSUID)                     │
  │                                │
  │◄─── VDC_SEND_ANNOUNCE_VDC ─────┤
  │◄─── VDC_SEND_ANNOUNCE_DEVICE ──┤
  │◄─── VDC_SEND_ANNOUNCE_DEVICE ──┤
  │    ...                         │
  │                                │
  Session Active - Normal Operation
```

## Testing

To test your implementation:

1. **Start the example vDC host:**
   ```bash
   python examples/simple_vdc_host.py
   ```

2. **Connect from a vdSM:**
   - Use a digitalSTROM Server (dSS) with vdSM capability
   - Or use a test client (see examples)

3. **Manual testing with netcat:**
   ```bash
   # Connect to the vDC host
   nc localhost 8444
   # Send Protocol Buffer messages (requires proper framing)
   ```

## dSUID Generation

In production, you must generate valid dSUIDs. Some approaches:

1. **From MAC address:**
   ```python
   import hashlib
   mac = "AA:BB:CC:DD:EE:FF"
   hash_input = f"macaddress:{mac}".encode()
   dsuid = hashlib.sha256(hash_input).hexdigest()[:34].upper()
   ```

2. **From UUID:**
   ```python
   import uuid
   import hashlib
   device_uuid = str(uuid.uuid4())
   hash_input = f"uuid:{device_uuid}".encode()
   dsuid = hashlib.sha256(hash_input).hexdigest()[:34].upper()
   ```

3. **Random (for testing only):**
   ```python
   import secrets
   dsuid = secrets.token_hex(17).upper()  # 34 hex chars
   ```

## Logging

The library uses Python's standard `logging` module. Configure it in your application:

```python
import logging

# Basic configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Or get specific logger
logger = logging.getLogger('ds_vdc_api')
logger.setLevel(logging.DEBUG)
```

## Service Discovery (Avahi)

For the vdSM to discover your vDC host, you need to announce it via mDNS/Avahi.

Create `/etc/avahi/services/ds-vdc.service`:

```xml
<?xml version="1.0" standalone='no'?>
<!DOCTYPE service-group SYSTEM "avahi-service.dtd">
<service-group>
  <name replace-wildcards="yes">My vDC on %h</name>
  <service protocol="ipv4">
    <type>_ds-vdc._tcp</type>
    <port>8444</port>
  </service>
</service-group>
```

Alternatively, use Python libraries like `python-zeroconf` for programmatic announcement.

## Troubleshooting

### Connection Issues

- **vdSM doesn't connect**: Check Avahi service is running and announcing
- **Connection refused**: Ensure port 8444 is not blocked by firewall
- **Connection drops**: Check network stability and ping/pong handling

### Message Issues

- **Invalid message**: Verify Protocol Buffer framing (2-byte length header)
- **Properties not returned**: Check property tree building
- **Scenes not working**: Verify device class supports scenes

### Debugging

Enable debug logging:

```python
import logging
logging.getLogger('ds_vdc_api').setLevel(logging.DEBUG)
```

Check the logs for detailed message flow.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Documentation

For detailed information about the vDC API:

- [Introduction](docs/01-introduction.md)
- [Quick Start Guide](docs/02-quickstart.md)
- [Core Concepts](docs/03-core-concepts.md)
- [Protocol Buffers Reference](docs/06-protobuf-reference.md)
- [Properties System](docs/07-properties.md)
- [Error Handling](docs/08-error-handling.md)

## License

This implementation is based on the digitalSTROM AG vDC API specifications.

## References

- Original proto file: `original_docs/genericVDC.proto`
- Documentation: `docs/` directory
- Examples: `examples/` directory
