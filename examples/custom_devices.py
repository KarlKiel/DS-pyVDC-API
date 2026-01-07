#!/usr/bin/env python3
"""
Custom device example - demonstrates creating a custom device class
"""

import logging
import time
from ds_vdc_api import VdcHost, VdcDevice

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SmartBulb(VdcDevice):
    """Custom smart bulb with color temperature control."""
    
    def __init__(self, dsuid: str, name: str):
        super().__init__(
            dsuid=dsuid,
            name=name,
            model="Smart Bulb Pro",
            model_uid="com.example.smartbulb.pro",
            device_class="Light"
        )
        
        # Additional state
        self.color_temperature = 2700  # Kelvin
        self.is_on = False
    
    def get_basic_properties(self):
        """Override to add color temperature property."""
        props = super().get_basic_properties()
        props["colorTemperature"] = self.color_temperature
        props["isOn"] = self.is_on
        return props
    
    def call_scene(self, scene: int, force: bool = False):
        """Override scene handling with custom behavior."""
        super().call_scene(scene, force)
        
        # Set on/off state based on output value
        self.is_on = self.output_value > 0
        
        logger.info(f"{self.name}: Scene {scene} -> {'ON' if self.is_on else 'OFF'} @ {self.output_value}%")
    
    def set_output_value(self, value: float, apply_now: bool = True):
        """Override output value setting."""
        super().set_output_value(value, apply_now)
        self.is_on = self.output_value > 0
        logger.info(f"{self.name}: Output set to {self.output_value}% ({'ON' if self.is_on else 'OFF'})")
    
    def set_color_temperature(self, temp_kelvin: int):
        """Set color temperature."""
        self.color_temperature = max(2000, min(6500, temp_kelvin))
        logger.info(f"{self.name}: Color temperature set to {self.color_temperature}K")
    
    def identify(self):
        """Flash the bulb to identify it."""
        logger.info(f"{self.name}: 💡 IDENTIFY - Flashing bulb!")
        # In a real implementation, this would trigger actual hardware


class SmartShade(VdcDevice):
    """Custom smart shade/blind device."""
    
    def __init__(self, dsuid: str, name: str):
        super().__init__(
            dsuid=dsuid,
            name=name,
            model="Smart Shade",
            model_uid="com.example.smartshade",
            device_class="Shade"
        )
        self.position = 0.0  # 0 = fully open, 100 = fully closed
    
    def call_scene(self, scene: int, force: bool = False):
        """Handle shade-specific scenes."""
        scene_positions = {
            0: 0.0,    # Fully open
            5: 100.0,  # Fully closed
            14: 25.0,  # 25% closed
            13: 50.0,  # 50% closed
            12: 75.0,  # 75% closed
        }
        
        if scene in scene_positions:
            self.position = scene_positions[scene]
            self.output_value = self.position
            logger.info(f"{self.name}: Moving to {self.position}% closed")
    
    def set_output_value(self, value: float, apply_now: bool = True):
        """Set shade position."""
        super().set_output_value(value, apply_now)
        self.position = self.output_value
        logger.info(f"{self.name}: Position set to {self.position}%")
    
    def identify(self):
        """Move the shade slightly to identify it."""
        logger.info(f"{self.name}: 🪟 IDENTIFY - Jogging shade!")


def main():
    """Run vDC host with custom devices."""
    
    # Create vDC host
    host = VdcHost(
        dsuid="DD000000000000000000000000000000DD",
        vdc_dsuid="EE000000000000000000000000000000EE",
        port=8444
    )
    
    # Create custom devices
    bulb1 = SmartBulb(
        dsuid="FF000000000000000000000000000000F1",
        name="Office Smart Bulb"
    )
    
    bulb2 = SmartBulb(
        dsuid="FF000000000000000000000000000000F2",
        name="Hallway Smart Bulb"
    )
    
    shade1 = SmartShade(
        dsuid="FF000000000000000000000000000000F3",
        name="Window Shade Left"
    )
    
    shade2 = SmartShade(
        dsuid="FF000000000000000000000000000000F4",
        name="Window Shade Right"
    )
    
    # Add devices
    host.add_device(bulb1)
    host.add_device(bulb2)
    host.add_device(shade1)
    host.add_device(shade2)
    
    logger.info("Custom device vDC host started")
    logger.info(f"Listening on port {host.port}")
    logger.info("Press Ctrl+C to stop\n")
    
    try:
        host.start(blocking=True)
    except KeyboardInterrupt:
        logger.info("\nShutting down...")
        host.stop()


if __name__ == "__main__":
    main()
