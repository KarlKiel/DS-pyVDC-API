# Session Management

This document describes how to manage vDC sessions - the connection lifecycle between a vdSM and vDC host.

## Session Basics

A **vDC session** is the logical connection between a vdSM (client) and a vDC host (server). The session is tied to the TCP connection lifetime.

**Key Principle:** Session lifetime = TCP connection lifetime

```
TCP Connect     → Session Start
TCP Active      → Session Active  
TCP Disconnect  → Session End
```

## Session States

```
┌──────────────┐
│ Disconnected │
└──────┬───────┘
       │ TCP Connect
       ▼
┌──────────────┐
│ Connected    │
└──────┬───────┘
       │ Hello Handshake
       ▼
┌──────────────┐
│ Initialized  │
└──────┬───────┘
       │ Announce vDC/Devices
       ▼
┌──────────────┐
│ Operational  │◄─┐
└──────┬───────┘  │ Normal Operation
       │          │
       │◄─────────┘
       │
       │ Bye/Disconnect
       ▼
┌──────────────┐
│ Terminated   │
└──────────────┘
```

## Session Initialization

### Step 1: TCP Connection

**vdSM initiates the connection** to the vDC host's TCP server socket.

```python
# vdSM (client) side
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((vdc_host_ip, vdc_host_port))  # Default port: 8444
```

```python
# vDC host (server) side
import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('0.0.0.0', 8444))
server.listen(1)

client_sock, addr = server.accept()
# New session begins
```

### Step 2: Hello Handshake

After TCP connection, perform the hello handshake:

**vdSM sends hello request:**
```
Message {
    type = VDSM_REQUEST_HELLO
    message_id = 1
    vdsm_request_hello {
        dSUID = "<vdSM's dSUID>"
        api_version = 3
    }
}
```

**vDC responds with hello response:**
```
Message {
    type = VDC_RESPONSE_HELLO
    message_id = 1
    vdc_response_hello {
        dSUID = "<vDC host's dSUID>"
    }
}
```

**On success:** Session is initialized, proceed to operation

**On error:** Return `GenericResponse` with error code:
- `ERR_INCOMPATIBLE_API` - API version not supported
- `ERR_SERVICE_NOT_AVAILABLE` - Already connected to another vdSM
- `ERR_MESSAGE_UNKNOWN` - Invalid message format

### Step 3: vDC and Device Announcement

After successful hello, vDC must announce itself and its devices:

```
# Announce the vDC itself
vDC → vdSM: VDC_SEND_ANNOUNCE_VDC {
    dSUID = "<vDC's dSUID>"
}

# Announce each device
vDC → vdSM: VDC_SEND_ANNOUNCE_DEVICE {
    dSUID = "<device1's dSUID>"
    vdc_dSUID = "<vDC's dSUID>"
}

vDC → vdSM: VDC_SEND_ANNOUNCE_DEVICE {
    dSUID = "<device2's dSUID>"
    vdc_dSUID = "<vDC's dSUID>"
}
```

**Important:** After reconnection, ALL devices must be re-announced.

### Complete Initialization Sequence

```
vdSM                                    vDC Host
  │                                         │
  ├──────── TCP Connect ──────────────────►│
  │                                         │
  ├──────── VDSM_REQUEST_HELLO ───────────►│
  │         (api_version=3, dSUID)         │
  │                                         │
  │◄──────── VDC_RESPONSE_HELLO ───────────┤
  │          (dSUID)                        │
  │                                         │
  │◄──────── VDC_SEND_ANNOUNCE_VDC ────────┤
  │          (vDC dSUID)                    │
  │                                         │
  │◄──────── VDC_SEND_ANNOUNCE_DEVICE ─────┤
  │          (device1 dSUID, vDC dSUID)     │
  │                                         │
  │◄──────── VDC_SEND_ANNOUNCE_DEVICE ─────┤
  │          (device2 dSUID, vDC dSUID)     │
  │                                         │
  │   Session now operational               │
  │                                         │
```

## Session Operation

During normal operation, the session handles:

### 1. Request/Response Exchanges

**Pattern:** vdSM sends request, vDC responds

**Example: Property Query**
```
vdSM → vDC: VDSM_REQUEST_GET_PROPERTY (message_id=42)
vDC → vdSM: VDC_RESPONSE_GET_PROPERTY (message_id=42)
```

**Message ID matching:** Response has same `message_id` as request

### 2. Notifications

**Pattern:** vdSM sends notification, vDC executes (no response except on error)

**Example: Scene Call**
```
vdSM → vDC: VDSM_NOTIFICATION_CALL_SCENE
# No response unless error occurs
```

### 3. Push Updates

**Pattern:** vDC proactively sends state changes to vdSM

**Example: Device State Change**
```
vDC → vdSM: VDC_SEND_PUSH_NOTIFICATION {
    dSUID = "<device dSUID>"
    changedproperties = [...]
}
```

⚠️ **Note:** `VDC_SEND_PUSH_PROPERTY` is deprecated, use push notifications instead

### 4. Presence Monitoring

**Pattern:** vdSM pings to check if vDC is responsive

```
vdSM → vDC: VDSM_SEND_PING {
    dSUID = "<vDC or device dSUID>"
}

vDC → vdSM: VDC_SEND_PONG {
    dSUID = "<same dSUID>"
}
```

**Timeout:** If no pong received within reasonable time (e.g., 10 seconds), consider connection lost

## Session Termination

### Graceful Shutdown

**vdSM-initiated:**
```
vdSM → vDC: VDSM_SEND_BYE {
    dSUID = "<vdSM dSUID>"
}
# Then close TCP connection
```

**vDC-initiated:**
```
vDC: Close TCP connection
```

### Ungraceful Termination

**Network failure, crash, or forced disconnect:**
- TCP connection breaks
- Session immediately ends
- No bye message sent
- Both sides must detect and handle

## Reconnection

After session termination, a new session must be established from scratch:

### Reconnection Steps

1. **Detect disconnection**
   - TCP socket error
   - Ping timeout
   - Connection closed

2. **Clean up old session**
   - Close socket
   - Clear session state
   - Mark devices as disconnected

3. **Wait before reconnecting** (exponential backoff)
   ```python
   delay = min(2 ** attempt, 60)  # Max 60 seconds
   time.sleep(delay)
   ```

4. **Re-establish TCP connection**
   ```python
   sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   sock.connect((host, port))
   ```

5. **Perform hello handshake**
   - Send `VDSM_REQUEST_HELLO`
   - Wait for `VDC_RESPONSE_HELLO`

6. **Re-announce everything**
   - Announce vDC(s)
   - Announce all devices
   - Restore session state

### Reconnection Example

```python
class VdcSession:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.attempt = 0
    
    def connect(self):
        """Connect with exponential backoff"""
        while not self.connected:
            try:
                # Exponential backoff
                if self.attempt > 0:
                    delay = min(2 ** self.attempt, 60)
                    logger.info(f"Waiting {delay}s before reconnect...")
                    time.sleep(delay)
                
                # TCP connect
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.host, self.port))
                
                # Hello handshake
                self.send_hello()
                response = self.receive_message()
                
                if response.type == Type.VDC_RESPONSE_HELLO:
                    # Success!
                    self.connected = True
                    self.attempt = 0
                    
                    # Re-announce
                    self.announce_vdc()
                    self.announce_all_devices()
                    
                    logger.info("Session established")
                    return True
                else:
                    # Unexpected response
                    self.socket.close()
                    self.attempt += 1
                    
            except Exception as e:
                logger.error(f"Connection failed: {e}")
                if self.socket:
                    self.socket.close()
                self.attempt += 1
        
        return False
    
    def disconnect(self):
        """Gracefully close session"""
        if self.connected:
            try:
                # Send bye
                self.send_bye()
                # Close socket
                self.socket.close()
            except:
                pass
            finally:
                self.connected = False
                self.socket = None
```

## Connection Management Best Practices

### 1. Exclusive Connections

**One vdSM per vDC host:**
- vDC host should only accept one vdSM connection at a time
- Return `ERR_SERVICE_NOT_AVAILABLE` if already connected
- Reject new connections until current session ends

```python
class VdcHost:
    def __init__(self):
        self.current_session = None
    
    def accept_connection(self, client_socket):
        if self.current_session and self.current_session.is_active():
            # Already connected
            error = create_error_response(ERR_SERVICE_NOT_AVAILABLE)
            send_message(client_socket, error)
            client_socket.close()
            return
        
        # Accept new session
        self.current_session = Session(client_socket)
```

### 2. Heartbeat/Keepalive

Implement regular ping/pong to detect connection issues:

```python
# vdSM side
def heartbeat_loop(self):
    """Send ping every 30 seconds"""
    while self.connected:
        time.sleep(30)
        try:
            self.send_ping()
            # Wait for pong with timeout
            response = self.receive_message(timeout=10)
            if response.type != Type.VDC_SEND_PONG:
                logger.warning("Pong not received, connection may be lost")
                self.handle_disconnect()
        except TimeoutError:
            logger.error("Ping timeout, connection lost")
            self.handle_disconnect()
```

### 3. Message ID Management

Track message IDs for request/response matching:

```python
class MessageIdManager:
    def __init__(self):
        self.next_id = 1
        self.pending = {}  # message_id -> callback
    
    def get_next_id(self):
        """Get next message ID"""
        msg_id = self.next_id
        self.next_id += 1
        if self.next_id > 0xFFFFFFFF:  # uint32 max
            self.next_id = 1
        return msg_id
    
    def send_request(self, message, callback):
        """Send request and register callback"""
        msg_id = self.get_next_id()
        message.message_id = msg_id
        self.pending[msg_id] = callback
        self.send_message(message)
    
    def handle_response(self, message):
        """Match response to request"""
        msg_id = message.message_id
        if msg_id in self.pending:
            callback = self.pending.pop(msg_id)
            callback(message)
        else:
            logger.warning(f"Unexpected response: {msg_id}")
```

### 4. State Persistence

Maintain session state for recovery:

```python
class SessionState:
    def __init__(self):
        self.vdc_dsuid = None
        self.vdc_host_dsuid = None
        self.devices = {}  # dSUID -> device info
        self.announced_devices = set()
    
    def on_device_announced(self, device_dsuid, vdc_dsuid):
        """Track announced devices"""
        self.announced_devices.add(device_dsuid)
        self.devices[device_dsuid] = {
            'vdc_dsuid': vdc_dsuid,
            'announced': True
        }
    
    def on_reconnect(self):
        """Re-announce all devices after reconnect"""
        for dsuid in self.announced_devices:
            self.send_announce_device(dsuid, self.devices[dsuid]['vdc_dsuid'])
```

### 5. Error Recovery

Handle errors gracefully:

```python
def handle_error(self, error_response):
    """Handle different error types"""
    code = error_response.code
    error_type = error_response.errorType
    
    if error_type == ERROR_TYPE_DISCONNECTED:
        # Connection lost, reconnect
        self.reconnect()
    
    elif error_type == ERROR_TYPE_OVERLOADED:
        # Back off and retry
        time.sleep(5)
        return self.retry_operation()
    
    elif code == ERR_SERVICE_NOT_AVAILABLE:
        # Already connected, wait longer
        time.sleep(30)
        return self.reconnect()
    
    elif code == ERR_INCOMPATIBLE_API:
        # Version mismatch, can't recover
        logger.error("API version incompatible, cannot connect")
        return False
    
    else:
        # Other errors
        logger.error(f"Error: {code} - {error_response.description}")
        return False
```

## Advanced Topics

### Multiple vDCs per Host

A single vDC host can host multiple logical vDCs:

```python
class VdcHost:
    def __init__(self):
        self.vdcs = {
            'lighting_vdc': LightingVdc(),
            'sensor_vdc': SensorVdc()
        }
    
    def announce_all_vdcs(self):
        """Announce each vDC"""
        for vdc_id, vdc in self.vdcs.items():
            self.send_announce_vdc(vdc.dsuid)
            
            # Announce devices for this vDC
            for device in vdc.devices:
                self.send_announce_device(device.dsuid, vdc.dsuid)
```

### Session Timeout

Implement session timeout for inactive connections:

```python
class Session:
    def __init__(self, socket):
        self.socket = socket
        self.last_activity = time.time()
        self.timeout = 300  # 5 minutes
    
    def check_timeout(self):
        """Check if session timed out"""
        if time.time() - self.last_activity > self.timeout:
            logger.warning("Session timeout, closing")
            self.close()
            return True
        return False
    
    def on_activity(self):
        """Reset timeout on activity"""
        self.last_activity = time.time()
```

## What's Next?

- **[Device Integration](12-device-integration.md)** - Implementing device functionality
- **[Discovery and Announcement](14-discovery.md)** - Service discovery details
- **[Error Handling](10-error-handling.md)** - Handling errors in sessions

---

**Related:**
- [Protocol Buffers](09-protobuf-reference.md) - Message formats
- [API Messages](07-api-messages.md) - Detailed message reference
- [Quick Start](02-quickstart.md) - Basic session implementation
