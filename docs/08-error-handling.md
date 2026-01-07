# Error Handling

This document describes error handling in the vDC API, including error codes, error types, and recovery strategies.

## Generic Response

When a vDC operation fails, the vDC returns a **GenericResponse** message containing error information.

### GenericResponse Structure

```protobuf
message GenericResponse {
    required ResultCode code = 1 [default = ERR_OK];
    optional string description = 2;
}
```

**In Practice**, GenericResponse contains additional fields for error handling:

| Field | Type | Purpose |
|-------|------|---------|
| `code` | integer | Numerical result code (see Error Codes) |
| `errorType` | integer | Category of failure for error recovery logic |
| `description` | string | Developer-oriented explanation (not for end users) |
| `userMessageToBeTranslated` | string | User-friendly message suitable for UI display |

### Usage Guidelines

**For Program Logic:**
- Use `errorType` to determine recovery strategy
- Use `code` for specific error identification
- Use `userMessageToBeTranslated` for user-facing messages

**For Debugging:**
- Use `description` for detailed diagnostics
- Log both `code` and `description`
- Don't display `description` to end users

## Error Codes (ResultCode)

All error codes are defined in the `ResultCode` enum:

### ERR_OK (0)
**Meaning:** Everything is OK, no error

**When Used:** Successful operations

**Action:** Continue normally

---

### ERR_MESSAGE_UNKNOWN (1)
**Meaning:** The message type is unknown

**Causes:**
- vDC doesn't recognize the message type
- API version mismatch
- Incomplete implementation
- Protocol buffer parsing error

**Recovery:**
- Check API version compatibility
- Verify message type is supported
- Update vDC implementation if needed

---

### ERR_INCOMPATIBLE_API (2)
**Meaning:** API version is not compatible

**Causes:**
- vdSM and vDC have incompatible API versions
- vDC doesn't support requested API version

**Recovery:**
- Check API version in hello handshake
- Upgrade vDC to support newer API
- Use compatible API version if possible

**Critical:** This error should occur during session initialization

---

### ERR_SERVICE_NOT_AVAILABLE (3)
**Meaning:** The vDC service cannot respond

**Causes:**
- vDC host already connected to another vdSM
- vDC is in maintenance mode
- vDC is shutting down
- Resource constraints

**Recovery:**
- Wait and retry connection later
- Check if another vdSM is connected
- Verify vDC host status
- Use exponential backoff for retries

---

### ERR_INSUFFICIENT_STORAGE (4)
**Meaning:** Cannot store data due to storage limitations

**Causes:**
- Device storage full
- Scene table full
- Configuration storage exceeded
- Memory allocation failed

**Recovery:**
- Free up storage on device
- Delete unused scenes/configurations
- Check device capacity limits
- May require user intervention

---

### ERR_FORBIDDEN (5)
**Meaning:** The operation is not allowed

**Causes:**
- Operation not permitted in current state
- Insufficient privileges
- Configuration prevents operation
- Safety/security restrictions

**Recovery:**
- Check operation prerequisites
- Verify device state allows operation
- Review access permissions
- Consult device documentation

---

### ERR_NOT_IMPLEMENTED (6)
**Meaning:** Feature not (yet) implemented

**Causes:**
- Optional feature not supported
- Future functionality
- Device limitations

**Recovery:**
- Use alternative approach if available
- Check device capabilities
- Don't rely on this feature
- Document limitation

**Note:** This is not an error for optional features; it's informational

---

### ERR_NO_CONTENT_FOR_ARRAY (7)
**Meaning:** Array data was expected but not provided

**Causes:**
- Missing array elements in request
- Empty array where content required
- Property query expected multiple elements

**Recovery:**
- Provide required array data
- Check message structure
- Verify protocol buffer definition

---

### ERR_INVALID_VALUE_TYPE (8)
**Meaning:** Invalid data type

**Causes:**
- Wrong type in PropertyValue
- Type mismatch in property assignment
- Invalid enum value
- Data format error

**Recovery:**
- Check data types in request
- Verify property type expectations
- Use correct PropertyValue variant
- Validate enum values

---

### ERR_MISSING_SUBMESSAGE (9)
**Meaning:** Expected submessage is missing

**Causes:**
- Required nested message not provided
- Incomplete protocol buffer message
- Missing required field

**Recovery:**
- Include required submessage
- Check message structure
- Verify protocol definition

---

### ERR_MISSING_DATA (10)
**Meaning:** Additional data was expected

**Causes:**
- Required field missing
- Incomplete message
- Missing parameters

**Recovery:**
- Provide all required fields
- Check message completeness
- Verify protocol requirements

---

### ERR_NOT_FOUND (11)
**Meaning:** Addressed entity or object not found

**Causes:**
- Invalid dSUID
- Device doesn't exist
- Property path doesn't exist
- Resource was removed

**Recovery:**
- Verify dSUID is correct
- Check device still exists
- Update device list
- Query available resources

---

### ERR_NOT_AUTHORIZED (12)
**Meaning:** Caller is not authorized

**Causes:**
- Authentication required
- Insufficient permissions
- Device in locked state
- Native device access control

**Recovery:**
- Perform authentication
- Check authorization level
- Unlock device if needed
- May require user intervention

---

## Error Types

Error types categorize failures for recovery strategy:

### ERROR_TYPE_FAILED (0)
**Meaning:** Generic failure

**Characteristics:**
- Default error type
- Operation failed for unspecified reason
- No specific recovery strategy

**Recovery:**
- Check error description
- May or may not be retryable
- Use error code for specifics

---

### ERROR_TYPE_OVERLOADED (1)
**Meaning:** Temporary resource shortage

**Characteristics:**
- Operation failed due to lack of resources
- Temporary condition
- Will likely succeed later
- **Should NOT retry immediately**

**Recovery:**
- Wait before retrying
- Use exponential backoff
- Reduce request rate
- Check system load

**Example Scenarios:**
- Too many concurrent requests
- CPU overload
- Network congestion
- Temporary memory shortage

---

### ERROR_TYPE_DISCONNECTED (2)
**Meaning:** Connection lost

**Characteristics:**
- Communication failure
- Connection dropped
- Network issue
- Remote endpoint unavailable

**Recovery:**
- Re-establish connection
- Check network connectivity
- Verify remote device status
- May need to re-initialize session

**Example Scenarios:**
- TCP connection lost
- Device powered off
- Network cable unplugged
- WiFi disconnected

---

### ERROR_TYPE_UNIMPLEMENTED (3)
**Meaning:** Method not implemented

**Characteristics:**
- Requested feature not available
- Optional functionality
- May never be implemented

**Recovery:**
- Use fallback approach
- Check device capabilities
- Use alternative method
- Don't retry

**Example Scenarios:**
- Optional scene not supported
- Advanced feature unavailable
- Deprecated method
- Device-specific limitation

---

## Error Response Flow

### When Errors Are Sent

```
Request/Notification              Response Type
─────────────────────────────────────────────────
Request (expects specific response)
  ├─ Success → Specific response message
  └─ Failure → GenericResponse with error

Request (expects generic response)
  ├─ Success → GenericResponse (ERR_OK)
  └─ Failure → GenericResponse with error

Send (expects response only on error)
  ├─ Success → No response
  └─ Failure → GenericResponse with error

Notification (expects no response)
  ├─ Success → No response
  └─ Failure → No response (errors ignored)
```

### Message ID Matching

Responses include the `message_id` from the request:

```
Request:  message_id = 42
Response: message_id = 42
```

This allows matching responses to requests in asynchronous communication.

## Best Practices

### 1. Error Handling Strategy

```python
def handle_error(response):
    """Example error handling logic"""
    
    if response.code == ERR_OK:
        return True
    
    # Check error type for recovery strategy
    if response.errorType == ERROR_TYPE_OVERLOADED:
        # Wait and retry with backoff
        time.sleep(2 ** retry_count)
        return retry_operation()
    
    elif response.errorType == ERROR_TYPE_DISCONNECTED:
        # Re-establish connection
        reconnect()
        return retry_operation()
    
    elif response.errorType == ERROR_TYPE_UNIMPLEMENTED:
        # Use fallback method
        return try_alternative_approach()
    
    else:  # ERROR_TYPE_FAILED
        # Check specific error code
        if response.code == ERR_NOT_FOUND:
            # Resource doesn't exist
            log_error("Resource not found")
            return False
        elif response.code == ERR_FORBIDDEN:
            # Operation not allowed
            log_error("Operation forbidden")
            return False
        # ... handle other codes
```

### 2. Logging Errors

Always log errors with context:

```python
logger.error(
    f"vDC API Error: {error.code} - {error.description} "
    f"(type: {error.errorType}, message_id: {message_id})"
)
```

### 3. User-Facing Messages

Use `userMessageToBeTranslated` for UI:

```python
if error.code != ERR_OK:
    if error.userMessageToBeTranslated:
        show_user_message(translate(error.userMessageToBeTranslated))
    else:
        show_user_message(f"Error {error.code}: Operation failed")
```

### 4. Retry Logic

Implement smart retry with backoff:

```python
def retry_with_backoff(operation, max_retries=3):
    """Retry operation with exponential backoff"""
    for attempt in range(max_retries):
        response = operation()
        
        if response.code == ERR_OK:
            return response
        
        if response.errorType == ERROR_TYPE_OVERLOADED:
            # Exponential backoff
            delay = 2 ** attempt
            time.sleep(delay)
            continue
        
        elif response.errorType == ERROR_TYPE_UNIMPLEMENTED:
            # Don't retry unimplemented features
            return response
        
        else:
            # Other errors: retry with shorter delay
            time.sleep(1)
    
    return response  # Failed after all retries
```

### 5. Graceful Degradation

Handle missing features gracefully:

```python
response = call_advanced_feature()

if response.code == ERR_NOT_IMPLEMENTED:
    # Fall back to basic feature
    logger.info("Advanced feature not available, using basic feature")
    response = call_basic_feature()
```

## Common Error Scenarios

### Scenario 1: Device Not Found

**Cause:** dSUID doesn't exist or device removed

**Error:** `ERR_NOT_FOUND`

**Recovery:**
1. Refresh device list
2. Check device still announced
3. Verify dSUID spelling
4. Handle device removal gracefully

### Scenario 2: Connection Lost

**Cause:** Network failure or device disconnect

**Error:** `ERR_SERVICE_NOT_AVAILABLE` or `ERROR_TYPE_DISCONNECTED`

**Recovery:**
1. Detect connection loss
2. Attempt reconnection
3. Re-initialize session
4. Re-announce devices
5. Restore state

### Scenario 3: API Version Mismatch

**Cause:** vDC and vdSM have incompatible versions

**Error:** `ERR_INCOMPATIBLE_API`

**Recovery:**
1. Check supported API versions
2. Negotiate compatible version if possible
3. Upgrade vDC or vdSM
4. Document compatibility requirements

### Scenario 4: Storage Full

**Cause:** Device can't store more scenes or configuration

**Error:** `ERR_INSUFFICIENT_STORAGE`

**Recovery:**
1. Notify user
2. Request cleanup of old data
3. Reduce configuration complexity
4. May require device reset

## Testing Error Handling

### Test Cases

1. **Network Interruption**
   - Disconnect network during operation
   - Verify reconnection logic
   - Check state recovery

2. **Invalid Requests**
   - Send malformed messages
   - Use invalid dSUIDs
   - Verify error responses

3. **Resource Limits**
   - Fill device storage
   - Send concurrent requests
   - Test overload handling

4. **Unsupported Features**
   - Call unimplemented methods
   - Verify fallback behavior
   - Check error messages

## What's Next?

- **[Protocol Buffers Reference](06-protobuf-reference.md)** - Complete message reference
- **[Properties System](07-properties.md)** - Property-specific errors
- **[Session Management](05-session-management.md)** - Connection error handling
- **[Troubleshooting](10-troubleshooting.md)** - Debugging common issues

---

**Related:**
- [Protocol Buffers](06-protobuf-reference.md) - Message structure
- [Quick Start](02-quickstart.md) - Basic error handling examples
