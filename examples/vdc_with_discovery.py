#!/usr/bin/env python3
"""
Example: vDC host with Avahi/mDNS service announcement

This example shows how to announce your vDC host via Avahi/Bonjour
so that digitalSTROM servers can automatically discover it.

Requirements:
    - Avahi daemon running (Linux/macOS)
    - zeroconf package: pip install ds-vdc-api[discovery]
"""

import logging
import sys

# Check for optional zeroconf dependency
try:
    from zeroconf import ServiceInfo, Zeroconf
    ZEROCONF_AVAILABLE = True
except ImportError:
    ZEROCONF_AVAILABLE = False
    print("=" * 60)
    print("ERROR: zeroconf package not installed")
    print("This example requires the 'discovery' extra.")
    print("\nInstall it with:")
    print("  pip install ds-vdc-api[discovery]")
    print("or:")
    print("  pip install zeroconf")
    print("=" * 60)
    sys.exit(1)

from ds_vdc_api import VdcHost, VdcDevice

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class VdcHostWithDiscovery(VdcHost):
    """vDC Host with automatic service discovery via mDNS/Avahi"""
    
    def __init__(self, dsuid: str, vdc_dsuid: str, port: int = 8444, 
                 service_name: str = "Python vDC Host"):
        super().__init__(dsuid, vdc_dsuid, port)
        self.service_name = service_name
        self.zeroconf = None
        self.service_info = None
    
    def start_service_discovery(self):
        """Start mDNS service announcement"""
        import socket
        
        # Get local IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 80))
            local_ip = s.getsockname()[0]
        finally:
            s.close()
        
        # Create service info
        service_type = "_ds-vdc._tcp.local."
        service_name = f"{self.service_name}.{service_type}"
        
        self.service_info = ServiceInfo(
            service_type,
            service_name,
            addresses=[socket.inet_aton(local_ip)],
            port=self.port,
            properties={
                'vdcDsuid': self.vdc_dsuid,
                'vdcHostDsuid': self.dsuid,
            },
        )
        
        # Start Zeroconf
        self.zeroconf = Zeroconf()
        self.zeroconf.register_service(self.service_info)
        
        logger.info(f"✓ mDNS service announced: {service_name}")
        logger.info(f"  IP: {local_ip}")
        logger.info(f"  Port: {self.port}")
        logger.info(f"  Service type: {service_type}")
    
    def stop_service_discovery(self):
        """Stop mDNS service announcement"""
        if self.zeroconf and self.service_info:
            self.zeroconf.unregister_service(self.service_info)
            self.zeroconf.close()
            logger.info("✓ mDNS service unregistered")
    
    def start(self, blocking: bool = True):
        """Start with service discovery"""
        self.start_service_discovery()
        try:
            super().start(blocking=blocking)
        finally:
            self.stop_service_discovery()


def main():
    """Run vDC host with service discovery"""
    
    # Create host
    host = VdcHostWithDiscovery(
        dsuid="DD000000000000000000000000000000DD",
        vdc_dsuid="EE000000000000000000000000000000EE",
        port=8444,
        service_name="Python Smart Home vDC"
    )
    
    # Create some example devices
    devices = [
        VdcDevice(
            dsuid=f"FF000000000000000000000000000000{i:02X}",
            name=f"Smart Light {i+1}",
            model="Python Smart Bulb",
            model_uid="com.example.python.smartbulb",
            device_class="Light"
        )
        for i in range(5)
    ]
    
    for device in devices:
        host.add_device(device)
    
    logger.info(f"Starting vDC host with {len(devices)} devices")
    logger.info("The host will be discoverable via mDNS/Avahi")
    logger.info("digitalSTROM servers on the same network should find it automatically")
    logger.info("\nPress Ctrl+C to stop\n")
    
    try:
        host.start(blocking=True)
    except KeyboardInterrupt:
        logger.info("\nShutting down...")
        host.stop()


if __name__ == "__main__":
    main()
