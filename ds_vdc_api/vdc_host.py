"""
VDC Host implementation - manages vDC sessions and devices
"""

import socket
import logging
import threading
import time
from typing import Dict, Optional, List, Callable
from .genericVDC_pb2 import Message, Type, ResultCode, GenericResponse
from .message_handler import MessageHandler
from .vdc_device import VdcDevice
from .property_tree import build_property_tree, property_tree_to_dict


logger = logging.getLogger(__name__)


class VdcHost:
    """
    vDC Host server implementation.
    
    This class manages:
    - TCP server for vdSM connections
    - Session management (hello handshake, ping/pong)
    - Device announcements
    - Message routing and handling
    """
    
    def __init__(self, dsuid: str, vdc_dsuid: str, port: int = 8444):
        """
        Initialize a vDC Host.
        
        Args:
            dsuid: 34-character hexadecimal dSUID for the vDC host
            vdc_dsuid: 34-character hexadecimal dSUID for the vDC itself
            port: TCP port to listen on (default: 8444)
        """
        if len(dsuid) != 34:
            raise ValueError(f"Host dSUID must be 34 hex characters, got {len(dsuid)}")
        if len(vdc_dsuid) != 34:
            raise ValueError(f"vDC dSUID must be 34 hex characters, got {len(vdc_dsuid)}")
        
        self.dsuid = dsuid
        self.vdc_dsuid = vdc_dsuid
        self.port = port
        self.api_version = 3
        
        # Device registry
        self.devices: Dict[str, VdcDevice] = {}
        
        # Session state
        self.vdsm_dsuid: Optional[str] = None
        self.session_active = False
        self.next_message_id = 1
        
        # TCP server
        self.server_socket: Optional[socket.socket] = None
        self.client_socket: Optional[socket.socket] = None
        self.running = False
        
        # Message handler
        self.message_handler = MessageHandler()
        
    def add_device(self, device: VdcDevice) -> None:
        """
        Add a virtual device to this vDC host.
        
        Args:
            device: VdcDevice instance to add
        """
        device.vdc_dsuid = self.vdc_dsuid
        self.devices[device.dsuid] = device
        logger.info(f"Added device: {device.name} ({device.dsuid})")
        
        # If session is active, announce the device immediately
        if self.session_active and self.client_socket:
            self._announce_device(device)
    
    def remove_device(self, dsuid: str) -> None:
        """
        Remove a virtual device from this vDC host.
        
        Args:
            dsuid: dSUID of device to remove
        """
        if dsuid in self.devices:
            device = self.devices[dsuid]
            
            # Send vanish message if session active
            if self.session_active and self.client_socket:
                self._send_vanish(device)
            
            del self.devices[dsuid]
            logger.info(f"Removed device: {device.name} ({dsuid})")
    
    def start(self, blocking: bool = True) -> None:
        """
        Start the vDC host server.
        
        Args:
            blocking: If True, blocks until server stops. If False, runs in background thread.
        """
        self.running = True
        
        if blocking:
            self._run_server()
        else:
            thread = threading.Thread(target=self._run_server, daemon=True)
            thread.start()
    
    def stop(self) -> None:
        """Stop the vDC host server."""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        if self.client_socket:
            self.client_socket.close()
        logger.info("vDC Host stopped")
    
    def _run_server(self) -> None:
        """Main server loop - accepts connections and handles messages."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('0.0.0.0', self.port))
        self.server_socket.listen(1)
        
        logger.info(f"vDC Host listening on port {self.port}")
        
        while self.running:
            try:
                # Accept connection
                self.client_socket, address = self.server_socket.accept()
                logger.info(f"Connection from {address}")
                
                # Handle this client
                self._handle_client()
                
            except Exception as e:
                if self.running:
                    logger.error(f"Server error: {e}", exc_info=True)
    
    def _handle_client(self) -> None:
        """Handle a vdSM client connection."""
        try:
            self.session_active = False
            self.vdsm_dsuid = None
            
            while self.running:
                # Receive message
                msg = self.message_handler.receive_message(self.client_socket)
                if msg is None:
                    break
                
                logger.debug(f"Received message type: {Type.Name(msg.type)}")
                
                # Process message
                response = self._process_message(msg)
                
                # Send response if needed
                if response:
                    self.message_handler.send_message(self.client_socket, response)
                    logger.debug(f"Sent response type: {Type.Name(response.type)}")
        
        except Exception as e:
            logger.error(f"Client handler error: {e}", exc_info=True)
        
        finally:
            self.session_active = False
            if self.client_socket:
                self.client_socket.close()
                self.client_socket = None
            logger.info("Client disconnected")
    
    def _process_message(self, msg: Message) -> Optional[Message]:
        """
        Process an incoming message and return response.
        
        Args:
            msg: Received Message
            
        Returns:
            Response Message, or None if no response needed
        """
        if msg.type == Type.VDSM_REQUEST_HELLO:
            return self._handle_hello(msg)
        elif msg.type == Type.VDSM_REQUEST_GET_PROPERTY:
            return self._handle_get_property(msg)
        elif msg.type == Type.VDSM_REQUEST_SET_PROPERTY:
            return self._handle_set_property(msg)
        elif msg.type == Type.VDSM_SEND_PING:
            return self._handle_ping(msg)
        elif msg.type == Type.VDSM_SEND_BYE:
            return self._handle_bye(msg)
        elif msg.type == Type.VDSM_NOTIFICATION_CALL_SCENE:
            self._handle_call_scene(msg)
        elif msg.type == Type.VDSM_NOTIFICATION_SET_OUTPUT_CHANNEL_VALUE:
            self._handle_set_output_value(msg)
        elif msg.type == Type.VDSM_NOTIFICATION_DIM_CHANNEL:
            self._handle_dim_channel(msg)
        elif msg.type == Type.VDSM_NOTIFICATION_IDENTIFY:
            self._handle_identify(msg)
        elif msg.type == Type.VDSM_NOTIFICATION_SAVE_SCENE:
            self._handle_save_scene(msg)
        elif msg.type == Type.VDSM_NOTIFICATION_UNDO_SCENE:
            self._handle_undo_scene(msg)
        elif msg.type == Type.VDSM_REQUEST_GENERIC_REQUEST:
            return self._handle_generic_request(msg)
        else:
            logger.warning(f"Unhandled message type: {Type.Name(msg.type)}")
            return self._create_error_response(msg.message_id, ResultCode.ERR_NOT_IMPLEMENTED)
        
        return None
    
    def _handle_hello(self, msg: Message) -> Message:
        """Handle hello request from vdSM."""
        self.vdsm_dsuid = msg.vdsm_request_hello.dSUID
        api_version = msg.vdsm_request_hello.api_version
        
        logger.info(f"Hello from vdSM {self.vdsm_dsuid}, API version {api_version}")
        
        # Check API version compatibility
        if api_version > self.api_version:
            logger.warning(f"API version {api_version} may not be fully supported")
        
        # Send hello response
        response = Message()
        response.type = Type.VDC_RESPONSE_HELLO
        response.message_id = msg.message_id
        response.vdc_response_hello.dSUID = self.dsuid
        
        self.session_active = True
        
        # After hello, announce vDC and devices
        # These are sent after the hello response
        threading.Thread(target=self._announce_all, daemon=True).start()
        
        return response
    
    def _announce_all(self) -> None:
        """Announce vDC and all devices after session is established."""
        time.sleep(0.1)  # Small delay to ensure hello response is sent first
        
        if not self.client_socket or not self.session_active:
            return
        
        # Announce the vDC itself
        msg = Message()
        msg.type = Type.VDC_SEND_ANNOUNCE_VDC
        msg.message_id = 0  # Unsolicited
        msg.vdc_send_announce_vdc.dSUID = self.vdc_dsuid
        
        try:
            self.message_handler.send_message(self.client_socket, msg)
            logger.info(f"Announced vDC: {self.vdc_dsuid}")
        except Exception as e:
            logger.error(f"Failed to announce vDC: {e}")
            return
        
        # Announce all devices
        for device in self.devices.values():
            self._announce_device(device)
            time.sleep(0.05)  # Small delay between announcements
    
    def _announce_device(self, device: VdcDevice) -> None:
        """Announce a device to vdSM."""
        if not self.client_socket or not self.session_active:
            return
        
        msg = Message()
        msg.type = Type.VDC_SEND_ANNOUNCE_DEVICE
        msg.message_id = 0  # Unsolicited
        msg.vdc_send_announce_device.dSUID = device.dsuid
        msg.vdc_send_announce_device.vdc_dSUID = self.vdc_dsuid
        
        try:
            self.message_handler.send_message(self.client_socket, msg)
            logger.info(f"Announced device: {device.name} ({device.dsuid})")
        except Exception as e:
            logger.error(f"Failed to announce device {device.name}: {e}")
    
    def _send_vanish(self, device: VdcDevice) -> None:
        """Send vanish message for a device."""
        if not self.client_socket or not self.session_active:
            return
        
        msg = Message()
        msg.type = Type.VDC_SEND_VANISH
        msg.message_id = 0
        msg.vdc_send_vanish.dSUID = device.dsuid
        
        try:
            self.message_handler.send_message(self.client_socket, msg)
            logger.info(f"Sent vanish for device: {device.dsuid}")
        except Exception as e:
            logger.error(f"Failed to send vanish: {e}")
    
    def _handle_ping(self, msg: Message) -> Message:
        """Handle ping request."""
        response = Message()
        response.type = Type.VDC_SEND_PONG
        response.message_id = msg.message_id
        response.vdc_send_pong.dSUID = msg.vdsm_send_ping.dSUID
        return response
    
    def _handle_bye(self, msg: Message) -> None:
        """Handle bye message - graceful session termination."""
        logger.info("Received bye from vdSM")
        self.session_active = False
    
    def _handle_get_property(self, msg: Message) -> Message:
        """Handle get property request."""
        dsuid = msg.vdsm_request_get_property.dSUID
        query = msg.vdsm_request_get_property.query
        
        # Find the target (device, vDC, or vDC host)
        if dsuid == self.vdc_dsuid:
            # VDC properties
            properties = build_property_tree({
                "dSUID": self.vdc_dsuid,
                "type": "vDC",
                "name": "Virtual Device Connector",
                "model": "DS-pyVDC-API",
                "modelUID": "com.github.karlkiel.ds-pyvdc-api"
            })
        elif dsuid == self.dsuid:
            # VDC host properties
            properties = build_property_tree({
                "dSUID": self.dsuid,
                "type": "vDChost",
                "name": "Python vDC Host",
                "model": "DS-pyVDC-API Host",
            })
        elif dsuid in self.devices:
            # Device properties
            device = self.devices[dsuid]
            properties = device.get_property_tree(query)
        else:
            # Not found
            return self._create_error_response(msg.message_id, ResultCode.ERR_NOT_FOUND)
        
        # Build response
        response = Message()
        response.type = Type.VDC_RESPONSE_GET_PROPERTY
        response.message_id = msg.message_id
        response.vdc_response_get_property.properties.extend(properties)
        
        return response
    
    def _handle_set_property(self, msg: Message) -> Message:
        """Handle set property request."""
        dsuid = msg.vdsm_request_set_property.dSUID
        properties = msg.vdsm_request_set_property.properties
        
        # Find target device
        if dsuid in self.devices:
            device = self.devices[dsuid]
            
            # Convert property tree to dict for easier handling
            prop_dict = property_tree_to_dict(properties)
            
            # Apply properties
            for name, value in prop_dict.items():
                try:
                    device.set_property(name, value)
                except Exception as e:
                    logger.error(f"Failed to set property {name}: {e}")
                    return self._create_error_response(msg.message_id, ResultCode.ERR_INVALID_VALUE_TYPE)
            
            return self._create_success_response(msg.message_id)
        else:
            return self._create_error_response(msg.message_id, ResultCode.ERR_NOT_FOUND)
    
    def _handle_call_scene(self, msg: Message) -> None:
        """Handle call scene notification."""
        dsuids = msg.vdsm_send_call_scene.dSUID
        scene = msg.vdsm_send_call_scene.scene
        force = msg.vdsm_send_call_scene.force if msg.vdsm_send_call_scene.HasField('force') else False
        
        for dsuid in dsuids:
            if dsuid in self.devices:
                device = self.devices[dsuid]
                device.call_scene(scene, force)
                logger.info(f"Called scene {scene} on device {device.name}")
    
    def _handle_set_output_value(self, msg: Message) -> None:
        """Handle set output channel value notification."""
        dsuids = msg.vdsm_send_output_channel_value.dSUID
        value = msg.vdsm_send_output_channel_value.value
        apply_now = msg.vdsm_send_output_channel_value.apply_now
        
        for dsuid in dsuids:
            if dsuid in self.devices:
                device = self.devices[dsuid]
                device.set_output_value(value, apply_now)
                logger.info(f"Set output value {value} on device {device.name}")
    
    def _handle_dim_channel(self, msg: Message) -> None:
        """Handle dim channel notification."""
        dsuids = msg.vdsm_send_dim_channel.dSUID
        mode = msg.vdsm_send_dim_channel.mode
        channel = msg.vdsm_send_dim_channel.channel if msg.vdsm_send_dim_channel.HasField('channel') else 0
        
        for dsuid in dsuids:
            if dsuid in self.devices:
                device = self.devices[dsuid]
                device.dim_channel(mode, channel)
                logger.info(f"Dimming channel {channel} mode {mode} on device {device.name}")
    
    def _handle_identify(self, msg: Message) -> None:
        """Handle identify notification."""
        dsuids = msg.vdsm_send_identify.dSUID
        
        for dsuid in dsuids:
            if dsuid in self.devices:
                device = self.devices[dsuid]
                device.identify()
                logger.info(f"Identify requested for device {device.name}")
    
    def _handle_save_scene(self, msg: Message) -> None:
        """Handle save scene notification."""
        # Default implementation does nothing
        # Subclasses can override to implement scene saving
        logger.info("Save scene notification received (not implemented)")
    
    def _handle_undo_scene(self, msg: Message) -> None:
        """Handle undo scene notification."""
        # Default implementation does nothing
        logger.info("Undo scene notification received (not implemented)")
    
    def _handle_generic_request(self, msg: Message) -> Message:
        """Handle generic request (API v2c+)."""
        method_name = msg.vdsm_request_generic_request.methodname
        logger.info(f"Generic request: {method_name} (not implemented)")
        return self._create_error_response(msg.message_id, ResultCode.ERR_NOT_IMPLEMENTED)
    
    def _create_success_response(self, message_id: int) -> Message:
        """Create a generic success response."""
        response = Message()
        response.type = Type.GENERIC_RESPONSE
        response.message_id = message_id
        response.generic_response.code = ResultCode.ERR_OK
        return response
    
    def _create_error_response(self, message_id: int, error_code: ResultCode, 
                               description: str = "") -> Message:
        """Create a generic error response."""
        response = Message()
        response.type = Type.GENERIC_RESPONSE
        response.message_id = message_id
        response.generic_response.code = error_code
        if description:
            response.generic_response.description = description
        return response
