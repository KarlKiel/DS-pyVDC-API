"""Tests for utility functions."""

from ds_pyvdc_api.utils import validate_response, format_error


class TestUtils:
    """Test cases for utility functions."""

    def test_validate_response(self):
        """Test response validation."""
        response = {"status": "ok", "data": {}}
        result = validate_response(response)
        assert isinstance(result, bool)

    def test_format_error(self):
        """Test error formatting."""
        error = ValueError("test error")
        formatted = format_error(error)
        assert isinstance(formatted, str)
        assert "test error" in formatted
