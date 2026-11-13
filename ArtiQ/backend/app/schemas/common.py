from typing import Any


def api_response(
    success: bool,
    message: str,
    data: Any = None,
    error: str | None = None,
) -> dict:
    """Standardized JSON response envelope across all API endpoints."""
    return {
        "success": success,
        "message": message,
        "data": data,
        "error": error,
    }
