"""
DS-pyVDC-API - Python implementation of the digitalSTROM vDC API

This package provides a Python interface to implement vDC (Virtual Device Connector)
integrations with the digitalSTROM system.
"""

from .vdc_host import VdcHost
from .vdc_device import VdcDevice
from .message_handler import MessageHandler
from .property_tree import PropertyElement, PropertyValue, build_property_tree

__version__ = "1.0.0"
__all__ = [
    "VdcHost",
    "VdcDevice", 
    "MessageHandler",
    "PropertyElement",
    "PropertyValue",
    "build_property_tree",
]
