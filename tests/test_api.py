"""Tests for the VDC API client."""

from ds_pyvdc_api import VDCClient


class TestVDCClient:
    """Test cases for VDCClient class."""

    def test_client_initialization(self):
        """Test that VDCClient can be initialized."""
        client = VDCClient()
        assert client is not None

    def test_client_with_params(self):
        """Test VDCClient initialization with parameters."""
        base_url = "https://api.example.com"
        api_key = "test_key"
        client = VDCClient(base_url=base_url, api_key=api_key)
        assert client.base_url == base_url
        assert client.api_key == api_key

    def test_connect_method_exists(self):
        """Test that connect method exists."""
        client = VDCClient()
        assert hasattr(client, "connect")

    def test_disconnect_method_exists(self):
        """Test that disconnect method exists."""
        client = VDCClient()
        assert hasattr(client, "disconnect")
