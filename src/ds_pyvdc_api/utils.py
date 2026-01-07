"""Utility functions for DS-pyVDC-API."""

from typing import Any, Dict


def validate_response(response: Dict[str, Any]) -> bool:
    """Validate API response structure.

    Args:
        response (dict): The API response to validate.

    Returns:
        bool: True if response is valid, False otherwise.
    """
    # Placeholder for response validation logic
    return True


def format_error(error: Exception) -> str:
    """Format error messages in a consistent way.

    Args:
        error (Exception): The error to format.

    Returns:
        str: Formatted error message.
    """
    return f"Error: {str(error)}"
