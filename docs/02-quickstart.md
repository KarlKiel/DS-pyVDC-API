# Quick Start Guide

This guide will help you create your first vDC integration. We'll build a simple virtual device that connects to digitalSTROM.

## Prerequisites

Before starting, ensure you have:

- A digitalSTROM Server (dSS) with vdSM capability
- Network connectivity between your device and dSS
- Protocol Buffers compiler (`protoc`) installed
- Basic development environment (C, C++, Python, or any language with protobuf support)

## Step 1: Set Up Protocol Buffers

### Install protoc

```bash
# Ubuntu/Debian
sudo apt-get install protobuf-compiler

# macOS
brew install protobuf

# Or download from: https://github.com/protocolbuffers/protobuf/releases
```

### Compile the vDC Protocol Definition

Download or use the provided `genericVDC.proto` file:

```bash
# For C++
protoc --cpp_out=. genericVDC.proto

# For Python
protoc --python_out=. genericVDC.proto

# For other languages, see protobuf documentation
```

This generates the message classes you'll use to communicate with vdSM.

## Step 2: Implement Service Discovery

Your vDC host must announce itself using Avahi/Bonjour so the vdSM can find it.

### Create Avahi Service File

On Linux systems with avahi-daemon, create `/etc/avahi/services/ds-vdc.service`:

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

**Parameters:**
- `<name>`: Human-readable service name (replace with your device name)
- `<port>`: TCP port your vDC server will listen on (8444 is conventional)

### Alternative: Programmatic Announcement

If you can't use Avahi service files, use Avahi's D-Bus API or a library like `python-avahi` or `dns-sd`.

## Step 3: Create a TCP Server

Your vDC host needs to listen for incoming vdSM connections.

### Example: Python TCP Server Skeleton

```python
import socket
import struct
from genericVDC_pb2 import Message, Type

class VdcHost:
    def __init__(self, port=8444):
        self.port = port
        self.dsuid = "1234567890ABCDEF1234567890ABCD1234"  # Your vDC's dSUID
        
    def start(self):
        """Start the vDC host server"""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('0.0.0.0', self.port))
        server_socket.listen(1)
        
        print(f"vDC Host listening on port {self.port}")
        
        while True:
            client_socket, address = server_socket.accept()
            print(f"Connection from {address}")
            self.handle_client(client_socket)
    
    def handle_client(self, sock):
        """Handle a vdSM connection"""
        try:
            while True:
                # Read message
                msg = self.receive_message(sock)
                if msg is None:
                    break
                
                # Handle message
                response = self.process_message(msg)
                
                # Send response if needed
                if response:
                    self.send_message(sock, response)
        finally:
            sock.close()
    
    def receive_message(self, sock):
        """Receive a protobuf message from the socket"""
        # Read 2-byte length header
        header = sock.recv(2)
        if len(header) < 2:
            return None
        
        length = struct.unpack('!H', header)[0]  # Network byte order
        
        # Read message data
        data = b''
        while len(data) < length:
            chunk = sock.recv(length - len(data))
            if not chunk:
                return None
            data += chunk
        
        # Parse protobuf message
        msg = Message()
        msg.ParseFromString(data)
        return msg
    
    def send_message(self, sock, msg):
        """Send a protobuf message to the socket"""
        # Serialize message
        data = msg.SerializeToString()
        
        # Send length header (2 bytes, network byte order)
        header = struct.pack('!H', len(data))
        sock.sendall(header + data)
    
    def process_message(self, msg):
        """Process incoming message and return response"""
        if msg.type == Type.VDSM_REQUEST_HELLO:
            return self.handle_hello(msg)
        elif msg.type == Type.VDSM_REQUEST_GET_PROPERTY:
            return self.handle_get_property(msg)
        elif msg.type == Type.VDSM_SEND_PING:
            return self.handle_ping(msg)
        # Add more handlers as needed
        return None
    
    def handle_hello(self, msg):
        """Handle hello request from vdSM"""
        response = Message()
        response.type = Type.VDC_RESPONSE_HELLO
        response.message_id = msg.message_id
        response.vdc_response_hello.dSUID = self.dsuid
        return response
    
    def handle_ping(self, msg):
        """Handle ping request"""
        response = Message()
        response.type = Type.VDC_SEND_PONG
        response.message_id = msg.message_id
        response.vdc_send_pong.dSUID = msg.vdsm_send_ping.dSUID
        return response
    
    def handle_get_property(self, msg):
        """Handle property get request"""
        # TODO: Implement property tree
        response = Message()
        response.type = Type.VDC_RESPONSE_GET_PROPERTY
        response.message_id = msg.message_id
        # Add properties to response.vdc_response_get_property.properties
        return response

if __name__ == "__main__":
    host = VdcHost()
    host.start()
```

## Step 4: Implement Session Initialization

When a vdSM connects, you must handle the handshake sequence.

### Session Sequence

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
  Session Established              │
```

### Key Points

1. **API Version Check**: vdSM sends its API version in hello request
   - Current version is typically 3
   - Return `ERR_INCOMPATIBLE_API` if you can't support it

2. **dSUID Exchange**: Both sides exchange their dSUIDs
   - vDC host returns its dSUID in the response
   - Store the vdSM's dSUID for later use

## Step 5: Announce Your vDC

After session is established, announce the vDC itself to the system.

```python
def announce_vdc(self, sock):
    """Announce the vDC to vdSM"""
    msg = Message()
    msg.type = Type.VDC_SEND_ANNOUNCE_VDC
    msg.vdc_send_announce_vdc.dSUID = self.vdc_dsuid
    self.send_message(sock, msg)
```

## Step 6: Announce Virtual Devices

For each virtual device your vDC hosts, send an announcement.

```python
def announce_device(self, sock, device_dsuid, vdc_dsuid):
    """Announce a virtual device"""
    msg = Message()
    msg.type = Type.VDC_SEND_ANNOUNCE_DEVICE
    msg.vdc_send_announce_device.dSUID = device_dsuid
    msg.vdc_send_announce_device.vdc_dSUID = vdc_dsuid
    self.send_message(sock, msg)
```

**Important**: Each device needs a unique dSUID. See [Core Concepts](03-core-concepts.md#dSUIDs) for dSUID generation.

## Step 7: Implement Property System

The vdSM will query device properties. You need to respond with device information.

### Basic Properties

Every device must support these common properties:

```python
def get_device_properties(self, device):
    """Return basic device properties"""
    return {
        'dSUID': device.dsuid,
        'name': device.name,
        'model': device.model,
        'modelUID': device.model_uid,
        'type': 'vdSD',
        'deviceClass': 'Light',  # Or Shade, Heating, etc.
        # Add more properties as needed
    }
```

See [Properties System](08-properties.md) for complete property reference.

## Step 8: Handle Notifications

Implement handlers for notifications from vdSM (these don't require responses):

```python
def process_notification(self, msg):
    """Process notifications (no response needed)"""
    if msg.type == Type.VDSM_NOTIFICATION_CALL_SCENE:
        self.call_scene(msg.vdsm_send_call_scene)
    elif msg.type == Type.VDSM_NOTIFICATION_SET_OUTPUT_CHANNEL_VALUE:
        self.set_output_value(msg.vdsm_send_output_channel_value)
    # Add more notification handlers
```

## Step 9: Test Your Integration

### Using a Test vdSM

If you have access to a dSS:

1. Ensure your vDC host is running and announcing via Avahi
2. The dSS should automatically discover and connect
3. Check dSS logs for connection status
4. Your virtual devices should appear in the configurator

### Manual Testing

You can test with a simple TCP client:

```python
import socket
from genericVDC_pb2 import Message, vdsm_RequestHello, Type

# Connect to vDC host
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 8444))

# Send hello
msg = Message()
msg.type = Type.VDSM_REQUEST_HELLO
msg.message_id = 1
msg.vdsm_request_hello.dSUID = "VDSM_DSUID_HERE"
msg.vdsm_request_hello.api_version = 3

# Send (with length header)
data = msg.SerializeToString()
header = struct.pack('!H', len(data))
sock.sendall(header + data)

# Receive response
header = sock.recv(2)
length = struct.unpack('!H', header)[0]
data = sock.recv(length)

response = Message()
response.ParseFromString(data)
print(response)
```

## Common Pitfalls

### 1. **Incorrect Message Framing**
- Always send 2-byte length header in network byte order
- Maximum message size is 16384 bytes

### 2. **Missing Properties**
- Implement all required common properties
- Return empty result for unsupported properties (don't error)

### 3. **Wrong dSUID Format**
- dSUID must be exactly 34 hex characters (17 bytes)
- Use valid dSUID generation methods

### 4. **Avahi Not Running**
- Ensure avahi-daemon is running: `systemctl status avahi-daemon`
- Check service file is valid: `avahi-browse -a`

### 5. **Port Already in Use**
- Check if port is available: `netstat -tuln | grep 8444`
- Use SO_REUSEADDR socket option

## Next Steps

Now that you have a basic vDC running:

1. **Add Device Functionality**: Implement scene calls, dimming, etc.
2. **Implement More Properties**: See [Properties System](08-properties.md)
3. **Handle Error Cases**: See [Error Handling](10-error-handling.md)
4. **Add Multiple Devices**: Scale your vDC to host multiple devices
5. **Implement Push Notifications**: Send state changes proactively

## Example Projects

🔍 **MISSING**: Links to example projects using libdsvdc and vdcd

For complete implementation examples, see:
- [Examples](16-examples.md) - Complete code samples
- [Device Integration](12-device-integration.md) - Detailed implementation guide

## Troubleshooting

If things aren't working:

1. **Check Avahi**: `avahi-browse _ds-vdc._tcp`
2. **Check Logs**: Look for connection attempts in your vDC logs
3. **Verify Network**: Ensure vdSM can reach your vDC host
4. **Test Messages**: Use the manual test client above
5. **See**: [Troubleshooting](17-troubleshooting.md) for more help

---

**Next**: [Core Concepts](03-core-concepts.md) - Deep dive into digitalSTROM fundamentals
