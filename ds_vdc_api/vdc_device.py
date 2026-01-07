"""
Virtual Device representation for vDC API
"""

from typing import Dict, Any, Optional, List
from .genericVDC_pb2 import PropertyElement as PBPropertyElement
from .property_tree import build_property_tree


class VdcDevice:
    """
    Represents a virtual device in the vDC system.
    
    Each device has a unique dSUID and a set of properties that describe
    its capabilities, configuration, and current state.
    """
    
    def __init__(self, dsuid: str, name: str, model: str = "Generic Device",
                 model_uid: str = "vdc:generic", device_class: str = "Light"):
        """
        Initialize a virtual device.
        
        Args:
            dsuid: 34-character hexadecimal dSUID
            name: Human-readable device name
            model: Model name (default: "Generic Device")
            model_uid: Unique model identifier (default: "vdc:generic")
            device_class: Device class (default: "Light")
                         Valid: Light, Shade, Heating, Cooling, Ventilation,
                                Window, Joker, Audio, Video, SecuritySystem,
                                Access, SingleButton
        """
        if len(dsuid) != 34:
            raise ValueError(f"dSUID must be 34 hex characters, got {len(dsuid)}")
        
        self.dsuid = dsuid
        self.name = name
        self.model = model
        self.model_uid = model_uid
        self.device_class = device_class
        self.vdc_dsuid: Optional[str] = None
        
        # Device state
        self.output_value = 0.0
        self.output_mode = 0
        
        # Custom properties storage
        self._custom_properties: Dict[str, Any] = {}
    
    def get_basic_properties(self) -> Dict[str, Any]:
        """
        Get the basic common properties for this device.
        
        Returns:
            Dictionary of basic device properties
        """
        props = {
            "dSUID": self.dsuid,
            "name": self.name,
            "model": self.model,
            "modelUID": self.model_uid,
            "type": "vdSD",
            "deviceClass": self.device_class,
        }
        
        # Add custom properties
        props.update(self._custom_properties)
        
        return props
    
    def get_property_tree(self, query: Optional[List[PBPropertyElement]] = None) -> List[PBPropertyElement]:
        """
        Get property tree for this device, optionally filtered by query.
        
        Args:
            query: Optional list of PropertyElement objects specifying which properties to return
                   If None, returns all basic properties
        
        Returns:
            List of PropertyElement objects
        """
        # For simplicity, return all basic properties
        # A full implementation would filter based on query
        properties = self.get_basic_properties()
        
        # Add output state if applicable
        if self.device_class in ["Light", "Shade", "Heating", "Cooling"]:
            properties["output"] = {
                "value": self.output_value,
                "mode": self.output_mode
            }
        
        return build_property_tree(properties)
    
    def set_property(self, name: str, value: Any) -> None:
        """
        Set a property value on this device.
        
        Args:
            name: Property name
            value: New property value
        """
        if name == "name":
            self.name = value
        elif name in ["output.value", "outputValue"]:
            self.output_value = float(value)
        else:
            self._custom_properties[name] = value
    
    def call_scene(self, scene: int, force: bool = False) -> None:
        """
        Call a scene on this device.
        
        Override this method to implement device-specific scene behavior.
        
        Args:
            scene: Scene number (0-126)
            force: Force execution even if device has local priority
        """
        # Default implementation - map common scene numbers to output values
        scene_map = {
            0: 0.0,     # Off
            5: 100.0,   # On/Full
            14: 25.0,   # Scene 1 (25%)
            13: 50.0,   # Scene 2 (50%)
            12: 75.0,   # Scene 3 (75%)
        }
        
        if scene in scene_map:
            self.output_value = scene_map[scene]
    
    def set_output_value(self, value: float, apply_now: bool = True) -> None:
        """
        Set the output channel value.
        
        Args:
            value: Output value (typically 0.0-100.0)
            apply_now: Apply immediately (True) or stage for later (False)
        """
        if apply_now:
            self.output_value = value
    
    def dim_channel(self, mode: int, channel: int = 0) -> None:
        """
        Start/stop dimming a channel.
        
        Args:
            mode: Dim mode (0=stop, 1=up, -1=down)
            channel: Channel number (default: 0)
        """
        # Simple implementation - adjust by 10% per call
        if mode == 1:  # Dim up
            self.output_value = min(100.0, self.output_value + 10.0)
        elif mode == -1:  # Dim down
            self.output_value = max(0.0, self.output_value - 10.0)
        # mode == 0: stop dimming (no action needed)
    
    def identify(self) -> None:
        """
        Identify the device (e.g., blink, beep).
        
        Override this method to implement device-specific identification behavior.
        """
        # Default implementation does nothing
        # Subclasses should override to implement actual behavior
        pass
    
    def __repr__(self) -> str:
        return f"VdcDevice(dsuid={self.dsuid}, name={self.name}, class={self.device_class})"
