#!/usr/bin/env python3
"""
Test client that connects to a vDC host and performs basic operations
"""

import socket
import struct
import logging
import sys
import time
from ds_vdc_api.genericVDC_pb2 import Message, Type
from ds_vdc_api.message_handler import MessageHandler

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class VdsmTestClient:
    """Simple test client that acts as a vdSM to test vDC hosts"""
    
    def __init__(self, host: str = "localhost", port: int = 8444):
        self.host = host
        self.port = port
        self.dsuid = "VDSM0000000000000000000000000000SM"
        self.message_handler = MessageHandler()
        self.message_id = 1
        self.sock = None
    
    def connect(self):
        """Connect to vDC host"""
        logger.info(f"Connecting to {self.host}:{self.port}...")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        logger.info("Connected!")
    
    def send_hello(self):
        """Send hello request"""
        logger.info("Sending HELLO...")
        msg = Message()
        msg.type = Type.VDSM_REQUEST_HELLO
        msg.message_id = self.message_id
        self.message_id += 1
        msg.vdsm_request_hello.dSUID = self.dsuid
        msg.vdsm_request_hello.api_version = 3
        
        self.message_handler.send_message(self.sock, msg)
        
        # Receive response
        response = self.message_handler.receive_message(self.sock)
        if response.type == Type.VDC_RESPONSE_HELLO:
            logger.info(f"✓ Received HELLO response from: {response.vdc_response_hello.dSUID}")
            return True
        else:
            logger.error(f"✗ Unexpected response type: {Type.Name(response.type)}")
            return False
    
    def receive_announcements(self, count: int = 5, timeout: float = 2.0):
        """Receive device announcements"""
        logger.info(f"Waiting for announcements (timeout: {timeout}s)...")
        self.sock.settimeout(timeout)
        
        announcements = []
        try:
            for i in range(count):
                msg = self.message_handler.receive_message(self.sock)
                if msg is None:
                    break
                
                if msg.type == Type.VDC_SEND_ANNOUNCE_VDC:
                    logger.info(f"✓ Received vDC announcement: {msg.vdc_send_announce_vdc.dSUID}")
                    announcements.append(("vDC", msg.vdc_send_announce_vdc.dSUID))
                elif msg.type == Type.VDC_SEND_ANNOUNCE_DEVICE:
                    logger.info(f"✓ Received device announcement: {msg.vdc_send_announce_device.dSUID}")
                    announcements.append(("device", msg.vdc_send_announce_device.dSUID))
                else:
                    logger.info(f"Received: {Type.Name(msg.type)}")
        except socket.timeout:
            logger.info("Timeout reached, no more announcements")
        
        self.sock.settimeout(None)
        return announcements
    
    def get_property(self, dsuid: str, properties: list):
        """Get properties from a device"""
        logger.info(f"Getting properties from {dsuid}...")
        msg = Message()
        msg.type = Type.VDSM_REQUEST_GET_PROPERTY
        msg.message_id = self.message_id
        self.message_id += 1
        msg.vdsm_request_get_property.dSUID = dsuid
        
        # Add property queries
        for prop_name in properties:
            elem = msg.vdsm_request_get_property.query.add()
            elem.name = prop_name
        
        self.message_handler.send_message(self.sock, msg)
        
        # Receive response
        response = self.message_handler.receive_message(self.sock)
        if response.type == Type.VDC_RESPONSE_GET_PROPERTY:
            logger.info(f"✓ Received {len(response.vdc_response_get_property.properties)} properties")
            for prop in response.vdc_response_get_property.properties:
                value = None
                if prop.HasField('value'):
                    if prop.value.HasField('v_string'):
                        value = prop.value.v_string
                    elif prop.value.HasField('v_double'):
                        value = prop.value.v_double
                    elif prop.value.HasField('v_int64'):
                        value = prop.value.v_int64
                    elif prop.value.HasField('v_uint64'):
                        value = prop.value.v_uint64
                    elif prop.value.HasField('v_bool'):
                        value = prop.value.v_bool
                logger.info(f"  {prop.name} = {value}")
            return True
        else:
            logger.error(f"✗ Unexpected response: {Type.Name(response.type)}")
            return False
    
    def send_ping(self, dsuid: str):
        """Send ping to device"""
        logger.info(f"Sending PING to {dsuid}...")
        msg = Message()
        msg.type = Type.VDSM_SEND_PING
        msg.message_id = self.message_id
        self.message_id += 1
        msg.vdsm_send_ping.dSUID = dsuid
        
        self.message_handler.send_message(self.sock, msg)
        
        # Receive response
        response = self.message_handler.receive_message(self.sock)
        if response.type == Type.VDC_SEND_PONG:
            logger.info(f"✓ Received PONG from: {response.vdc_send_pong.dSUID}")
            return True
        else:
            logger.error(f"✗ Unexpected response: {Type.Name(response.type)}")
            return False
    
    def call_scene(self, dsuids: list, scene: int):
        """Call a scene on devices"""
        logger.info(f"Calling scene {scene} on {len(dsuids)} device(s)...")
        msg = Message()
        msg.type = Type.VDSM_NOTIFICATION_CALL_SCENE
        msg.message_id = 0  # Notifications use 0
        msg.vdsm_send_call_scene.dSUID.extend(dsuids)
        msg.vdsm_send_call_scene.scene = scene
        msg.vdsm_send_call_scene.force = False
        
        self.message_handler.send_message(self.sock, msg)
        logger.info("✓ Scene call sent (no response expected)")
    
    def disconnect(self):
        """Disconnect from vDC host"""
        if self.sock:
            logger.info("Disconnecting...")
            self.sock.close()
            logger.info("Disconnected")


def main():
    """Run test client"""
    client = VdsmTestClient()
    
    try:
        # Connect and handshake
        client.connect()
        if not client.send_hello():
            return 1
        
        # Receive announcements
        announcements = client.receive_announcements()
        
        if not announcements:
            logger.warning("No devices announced")
            return 0
        
        # Get first device
        devices = [dsuid for type_, dsuid in announcements if type_ == "device"]
        if devices:
            device_dsuid = devices[0]
            
            # Get device properties
            client.get_property(device_dsuid, ["dSUID", "name", "model", "deviceClass"])
            
            # Ping device
            client.send_ping(device_dsuid)
            
            # Call scene 5 (On/Full)
            client.call_scene([device_dsuid], 5)
            
            # Wait a bit
            time.sleep(1)
            
            # Call scene 0 (Off)
            client.call_scene([device_dsuid], 0)
        
        logger.info("\n✅ All tests completed successfully!")
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1
    finally:
        client.disconnect()


if __name__ == "__main__":
    sys.exit(main())
