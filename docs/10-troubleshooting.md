# Troubleshooting

Common issues and solutions when implementing or using the vDC API.

## Connection Issues

### vdSM Cannot Discover vDC Host

**Symptoms:**
- vdSM doesn't see vDC host
- No connection attempts
- Service not appearing in discovery

**Causes & Solutions:**

1. **Avahi daemon not running**
   ```bash
   # Check status
   sudo systemctl status avahi-daemon
   
   # Start if not running
   sudo systemctl start avahi-daemon
   ```

2. **Service file misconfigured**
   ```bash
   # Check service file exists
   ls /etc/avahi/services/ds-vdc.service
   
   # View announced services
   avahi-browse -a
   # Should show: _ds-vdc._tcp
   ```

3. **Firewall blocking mDNS**
   ```bash
   # Allow mDNS (port 5353 UDP)
   sudo ufw allow 5353/udp
   ```

4. **Wrong network/subnet**
   - Ensure vDC host and dSS are on same network
   - Check IP addresses are in same subnet
   - mDNS doesn't cross routers by default

5. **Service name collision**
   ```bash
   # Check for duplicate service names
   avahi-browse _ds-vdc._tcp
   # Each service should have unique name
   ```

**Debugging:**
```bash
# Monitor Avahi logs
journalctl -u avahi-daemon -f

# Test mDNS resolution
avahi-resolve -n <hostname>.local
```

---

### Connection Refused

**Symptoms:**
- vdSM finds vDC host but can't connect
- "Connection refused" error
- Immediate disconnect

**Causes & Solutions:**

1. **vDC host not listening**
   ```bash
   # Check if port is open
   netstat -tuln | grep 8444
   
   # Test connection locally
   telnet localhost 8444
   ```

2. **Wrong port number**
   - Check Avahi announcement matches actual port
   - Default is 8444, verify both match

3. **Firewall blocking TCP**
   ```bash
   # Allow vDC port
   sudo ufw allow 8444/tcp
   ```

4. **Already connected to another vdSM**
   - vDC host returns `ERR_SERVICE_NOT_AVAILABLE`
   - Check if another vdSM is connected
   - Close other connections first

**Debugging:**
```python
# Test with minimal client
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('192.168.1.100', 8444))
print("Connected!")
```

---

### Connection Drops Frequently

**Symptoms:**
- Connection established but drops after short time
- Reconnection loops
- Intermittent connectivity

**Causes & Solutions:**

1. **Network instability**
   ```bash
   # Check network quality
   ping -c 100 <vdc-host-ip>
   # Look for packet loss
   ```

2. **No heartbeat/keepalive**
   - Implement ping/pong mechanism
   - Send ping every 30 seconds
   - Detect unresponsive connections

3. **TCP socket timeout**
   ```python
   # Set socket keepalive
   sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
   
   # Tune TCP keepalive (Linux)
   sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 30)
   sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 10)
   sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 3)
   ```

4. **Resource exhaustion**
   - Check CPU/memory on vDC host
   - Monitor file descriptor usage
   - Look for memory leaks

**Debugging:**
```bash
# Monitor connection state
watch 'netstat -an | grep 8444'

# Check system resources
top
free -h
```

---

## Protocol Issues

### ERR_INCOMPATIBLE_API

**Symptoms:**
- Session initialization fails
- Error during hello handshake
- vDC rejects connection

**Causes & Solutions:**

1. **API version mismatch**
   ```python
   # vdSM sends api_version = 3
   # vDC only supports version 2
   
   # Solution: Update vDC to support version 3
   # Or negotiate compatible version
   ```

2. **Check API version**
   ```python
   # In hello response, check version
   if request.api_version > MAX_SUPPORTED_VERSION:
       return GenericResponse(code=ERR_INCOMPATIBLE_API)
   ```

**Debugging:**
- Log API versions from both sides
- Check documentation for version requirements
- Test with known compatible versions

---

### ERR_MESSAGE_UNKNOWN

**Symptoms:**
- vDC doesn't recognize message
- Unexpected response type
- Protocol errors

**Causes & Solutions:**

1. **Wrong message type**
   ```python
   # Check message type enum
   if msg.type not in SUPPORTED_TYPES:
       return GenericResponse(code=ERR_MESSAGE_UNKNOWN)
   ```

2. **Protobuf version mismatch**
   - Ensure same .proto file on both sides
   - Recompile after proto changes
   - Check protobuf library versions

3. **Corrupted message**
   - Verify message framing (2-byte length header)
   - Check network byte order
   - Validate message before parsing

**Debugging:**
```python
# Log raw message bytes
logger.debug(f"Received: {data.hex()}")

# Try parsing manually
try:
    msg = Message()
    msg.ParseFromString(data)
    logger.info(f"Type: {msg.type}")
except Exception as e:
    logger.error(f"Parse failed: {e}")
```

---

### Message Framing Errors

**Symptoms:**
- Parse errors
- Incomplete messages
- "Unexpected end of stream"

**Causes & Solutions:**

1. **Missing length header**
   ```python
   # WRONG
   sock.send(msg_data)
   
   # CORRECT
   length = len(msg_data)
   header = struct.pack('!H', length)  # Big-endian uint16
   sock.sendall(header + msg_data)
   ```

2. **Wrong byte order**
   ```python
   # WRONG
   header = struct.pack('H', length)  # Native byte order
   
   # CORRECT
   header = struct.pack('!H', length)  # Network (big-endian)
   ```

3. **Incomplete receive**
   ```python
   # WRONG - may not receive all data
   data = sock.recv(length)
   
   # CORRECT - ensure all data received
   data = b''
   while len(data) < length:
       chunk = sock.recv(length - len(data))
       if not chunk:
           raise ConnectionError("Connection closed")
       data += chunk
   ```

4. **Message too large**
   - Maximum message size: 16384 bytes
   - Split large data if needed
   - Return `ERR_INSUFFICIENT_STORAGE` if too large

**Debugging:**
```python
# Log message sizes
logger.debug(f"Sending {len(data)} bytes")

# Verify framing
header = sock.recv(2)
length = struct.unpack('!H', header)[0]
logger.debug(f"Expecting {length} bytes")
```

---

## Property Issues

### Properties Not Returned

**Symptoms:**
- getProperty returns empty
- Expected properties missing
- Incomplete property tree

**Causes & Solutions:**

1. **Property not implemented**
   - Optional properties may not exist
   - Check if property is supported
   - This is normal for optional properties

2. **Wrong property path**
   ```python
   # WRONG
   query.name = "Output.Value"  # Capital O
   
   # CORRECT
   query.name = "output"
   child.name = "value"
   ```

3. **Not traversing tree**
   ```python
   # Query nested property
   query = PropertyElement()
   query.name = "output"
   child = PropertyElement()
   child.name = "value"
   query.elements.append(child)
   ```

**Debugging:**
```python
# Request entire device tree
query = PropertyElement()
# Leave name empty for root
response = get_property(device_dsuid, [query])
# Examine full tree
print_property_tree(response.properties)
```

---

### ERR_NOT_FOUND on Property Write

**Symptoms:**
- setProperty fails
- Property exists but can't be written
- Error only on write, not read

**Causes & Solutions:**

1. **Read-only property**
   - Many properties are read-only
   - Check property access control
   - Common: dSUID, type, model, etc.

2. **Property doesn't exist**
   - Typo in property name
   - Property not implemented
   - Optional property not available

3. **Wrong value type**
   ```python
   # WRONG
   value.v_string = "75"  # Setting number as string
   
   # CORRECT
   value.v_double = 75.0
   ```

**Debugging:**
- First try reading the property
- Check property access (r vs r/w)
- Verify value type matches

---

## Device Issues

### Devices Not Appearing in dSS

**Symptoms:**
- Device announced but not visible
- dSS doesn't show device
- Device missing from configurator

**Causes & Solutions:**

1. **Device not announced**
   ```python
   # After session initialization:
   # 1. Announce vDC
   send_announce_vdc(vdc_dsuid)
   
   # 2. Announce each device
   send_announce_device(device_dsuid, vdc_dsuid)
   ```

2. **Wrong vDC dSUID**
   - `vdc_dSUID` in announce must match vDC's dSUID
   - Verify dSUID consistency

3. **Missing required properties**
   - Device must have: dSUID, name, model, modelUID, type
   - Check property implementation

4. **Device already exists**
   - dSUID collision with existing device
   - Ensure unique dSUIDs
   - Remove old device first

**Debugging:**
```python
# Log announcements
logger.info(f"Announcing vDC: {vdc_dsuid}")
logger.info(f"Announcing device: {device_dsuid} in vDC: {vdc_dsuid}")

# Verify properties
props = get_all_properties(device_dsuid)
logger.debug(f"Device properties: {props}")
```

---

### Scene Calls Not Working

**Symptoms:**
- Device receives scene call but doesn't respond
- Scene has no effect
- Wrong scene executed

**Causes & Solutions:**

1. **Not handling notification**
   ```python
   # Must handle VDSM_NOTIFICATION_CALL_SCENE
   if msg.type == Type.VDSM_NOTIFICATION_CALL_SCENE:
       scene_no = msg.vdsm_send_call_scene.scene
       self.execute_scene(scene_no)
   ```

2. **No scene values stored**
   - Device must store scene values
   - Check scene property implementation
   - Use defaults if no value saved

3. **Group mismatch**
   - Scene call includes group ID
   - Device must check if it's in that group
   - Filter calls by group membership

4. **Local priority active**
   - Device may have local priority set
   - Check `force` flag in scene call
   - Respect local priority unless forced

**Debugging:**
```python
# Log scene calls
logger.info(f"Scene call: scene={scene_no}, group={group_id}, force={force}")

# Verify scene values
for scene_no in range(128):
    value = self.get_scene_value(scene_no)
    logger.debug(f"Scene {scene_no}: {value}")
```

---

### Device Shows as Inactive

**Symptoms:**
- Device appears offline in dSS
- "Not active" status
- Red/warning indicator

**Causes & Solutions:**

1. **`active` property false**
   ```python
   # Set active to true when device is working
   self.active = True
   
   # Push update when status changes
   self.push_property_change("active", True)
   ```

2. **No ping response**
   ```python
   # Respond to pings
   if msg.type == Type.VDSM_SEND_PING:
       self.send_pong(msg.vdsm_send_ping.dSUID)
   ```

3. **Communication error**
   - Device unreachable
   - Network issue
   - Hardware problem

4. **Initialization failed**
   - Device failed to start
   - Check initialization logs
   - Verify hardware connection

---

## Performance Issues

### Slow Response Times

**Symptoms:**
- Long delays
- Timeout errors
- Sluggish behavior

**Causes & Solutions:**

1. **Synchronous operations**
   ```python
   # WRONG - blocking
   def get_property(name):
       return expensive_sync_call()
   
   # BETTER - async/threaded
   def get_property(name):
       return self.property_cache.get(name)
   ```

2. **No caching**
   - Cache property values
   - Update cache on changes
   - Invalidate when needed

3. **Network latency**
   - Minimize network round-trips
   - Batch operations where possible
   - Use push notifications

**Debugging:**
```python
# Time operations
import time
start = time.time()
response = operation()
elapsed = time.time() - start
logger.info(f"Operation took {elapsed:.2f}s")
```

---

### High CPU/Memory Usage

**Symptoms:**
- CPU at 100%
- Memory growing
- System slowdown

**Causes & Solutions:**

1. **Memory leak**
   ```python
   # Check for unreleased resources
   # Monitor object counts
   import gc
   print(gc.get_count())
   ```

2. **Busy loop**
   ```python
   # WRONG
   while True:
       check_something()
   
   # CORRECT
   while True:
       check_something()
       time.sleep(0.1)  # Don't busy-wait
   ```

3. **Large message processing**
   - Limit message sizes
   - Stream large data
   - Process in chunks

---

## Debugging Tools

### Enable Debug Logging

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('vdc')
logger.debug("Debug message")
```

### Network Capture

```bash
# Capture vDC traffic
sudo tcpdump -i any -w vdc.pcap port 8444

# Analyze with Wireshark
wireshark vdc.pcap
```

### Protocol Debugging

```python
# Log all messages
def log_message(direction, msg):
    logger.debug(f"{direction}: Type={msg.type}, ID={msg.message_id}")
    if msg.type == Type.GENERIC_RESPONSE:
        logger.debug(f"  Result: {msg.generic_response.code}")

# Before sending
log_message("SEND", msg)

# After receiving
log_message("RECV", msg)
```

### Test Client

Create a minimal test client:

```python
import socket
import struct
from genericVDC_pb2 import *

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 8444))

# Send hello
msg = Message()
msg.type = Type.VDSM_REQUEST_HELLO
msg.message_id = 1
msg.vdsm_request_hello.dSUID = "TEST_VDSM_DSUID"
msg.vdsm_request_hello.api_version = 3

data = msg.SerializeToString()
header = struct.pack('!H', len(data))
sock.sendall(header + data)

# Receive response
header = sock.recv(2)
length = struct.unpack('!H', header)[0]
data = sock.recv(length)

response = Message()
response.ParseFromString(data)
print(f"Response: {response}")
```

## Getting Help

If you're still stuck:

1. **Check logs** - Enable debug logging on both sides
2. **Verify basics** - Test network connectivity, service discovery
3. **Simplify** - Reduce to minimal test case
4. **Compare** - Check against working examples
5. **Document** - Write down what you've tried

**Remember:** Mark uncertainties clearly when documenting your findings!

---

**Related:**
- [Error Handling](08-error-handling.md) - Understanding error codes
- [Session Management](05-session-management.md) - Connection lifecycle
- [Quick Start](02-quickstart.md) - Basic implementation guide
