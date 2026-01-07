#!/usr/bin/env python3
"""
Simple vDC host example with virtual light devices
"""

import logging
import sys
import time
from ds_vdc_api import VdcHost, VdcDevice

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Run a simple vDC host with example devices."""
    
    # Create vDC host
    # Note: In production, generate proper dSUIDs
    host = VdcHost(
        dsuid="AA000000000000000000000000000000AA",  # vDC host dSUID
        vdc_dsuid="BB000000000000000000000000000000BB",  # vDC dSUID
        port=8444
    )
    
    # Create some virtual devices
    light1 = VdcDevice(
        dsuid="CC000000000000000000000000000000C1",
        name="Living Room Light",
        model="Virtual Light",
        model_uid="com.example.virtual.light",
        device_class="Light"
    )
    
    light2 = VdcDevice(
        dsuid="CC000000000000000000000000000000C2",
        name="Bedroom Light",
        model="Virtual Light",
        model_uid="com.example.virtual.light",
        device_class="Light"
    )
    
    light3 = VdcDevice(
        dsuid="CC000000000000000000000000000000C3",
        name="Kitchen Light",
        model="Virtual Dimmer",
        model_uid="com.example.virtual.dimmer",
        device_class="Light"
    )
    
    # Add devices to host
    host.add_device(light1)
    host.add_device(light2)
    host.add_device(light3)
    
    logger.info(f"Starting vDC host with {len(host.devices)} devices")
    logger.info("Devices:")
    for device in host.devices.values():
        logger.info(f"  - {device.name} ({device.dsuid})")
    
    logger.info(f"\nListening on port {host.port}")
    logger.info("Waiting for vdSM connection...")
    logger.info("Press Ctrl+C to stop\n")
    
    # Start the host (blocking)
    try:
        host.start(blocking=True)
    except KeyboardInterrupt:
        logger.info("\nShutting down...")
        host.stop()
        sys.exit(0)


if __name__ == "__main__":
    main()
