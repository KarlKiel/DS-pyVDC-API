"""
Message handler for vDC protocol - handles serialization, framing and I/O
"""

import struct
import socket
from typing import Optional
from .genericVDC_pb2 import Message


class MessageHandler:
    """Handles Protocol Buffer message framing for vDC communication"""
    
    MAX_MESSAGE_SIZE = 16384  # 16 KB maximum message size
    
    @staticmethod
    def receive_message(sock: socket.socket) -> Optional[Message]:
        """
        Receive a protobuf message from the socket.
        
        Messages are framed with a 2-byte length header (network byte order).
        
        Args:
            sock: Socket to receive from
            
        Returns:
            Parsed Message object, or None if connection closed
        """
        # Read 2-byte length header
        header = sock.recv(2)
        if len(header) < 2:
            return None
        
        length = struct.unpack('!H', header)[0]  # Network byte order (big-endian)
        
        if length > MessageHandler.MAX_MESSAGE_SIZE:
            raise ValueError(f"Message size {length} exceeds maximum {MessageHandler.MAX_MESSAGE_SIZE}")
        
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
    
    @staticmethod
    def send_message(sock: socket.socket, msg: Message) -> None:
        """
        Send a protobuf message to the socket.
        
        Messages are framed with a 2-byte length header (network byte order).
        
        Args:
            sock: Socket to send to
            msg: Message to send
        """
        # Serialize message
        data = msg.SerializeToString()
        
        if len(data) > MessageHandler.MAX_MESSAGE_SIZE:
            raise ValueError(f"Message size {len(data)} exceeds maximum {MessageHandler.MAX_MESSAGE_SIZE}")
        
        # Send length header (2 bytes, network byte order) + message data
        header = struct.pack('!H', len(data))
        sock.sendall(header + data)
