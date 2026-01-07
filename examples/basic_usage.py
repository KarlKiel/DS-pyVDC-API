"""Basic usage example for DS-pyVDC-API."""

from ds_pyvdc_api import VDCClient


def main():
    """Demonstrate basic usage of the VDC API client."""
    # Initialize the client
    client = VDCClient(base_url="https://api.example.com", api_key="your_api_key_here")

    # Connect to the API
    print("Connecting to VDC API...")
    client.connect()

    # Your API operations would go here
    print("Connected! Ready to perform VDC operations.")

    # Disconnect when done
    print("Disconnecting...")
    client.disconnect()
    print("Done!")


if __name__ == "__main__":
    main()
