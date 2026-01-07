"""Example showing configuration usage."""

from ds_pyvdc_api import VDCClient
from ds_pyvdc_api.config import Config


def main():
    """Demonstrate configuration usage."""
    # Create a configuration
    config = Config()
    config.base_url = "https://api.example.com"
    config.api_key = "your_api_key_here"
    config.timeout = 60
    config.verify_ssl = True

    # Validate the configuration
    if config.validate():
        print("Configuration is valid!")

        # Use the configuration with the client
        client = VDCClient(base_url=config.base_url, api_key=config.api_key)

        print(f"Client initialized with configuration: {client}")
    else:
        print("Configuration is invalid!")


if __name__ == "__main__":
    main()
