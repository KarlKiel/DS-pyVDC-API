"""Custom exceptions for DS-pyVDC-API."""


class VDCAPIError(Exception):
    """Base exception for all VDC API errors."""

    pass


class ConnectionError(VDCAPIError):
    """Raised when connection to VDC API fails."""

    pass


class AuthenticationError(VDCAPIError):
    """Raised when authentication fails."""

    pass


class InvalidConfigError(VDCAPIError):
    """Raised when configuration is invalid."""

    pass


class APIResponseError(VDCAPIError):
    """Raised when API returns an unexpected response."""

    pass
