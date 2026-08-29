from typing import Any, Dict, Optional

from fastapi.responses import JSONResponse


# =========================================================
# SUCCESS RESPONSE
# =========================================================

def success_response(
    message: str,
    data: Any = None,
    status_code: int = 200,
) -> JSONResponse:
    """
    Create a standardized successful API response.

    Example:

    {
        "success": true,
        "message": "Document scan completed",
        "data": {...},
        "error": null
    }
    """

    response = {
        "success": True,
        "message": message,
        "data": data,
        "error": None,
    }

    return JSONResponse(
        status_code=status_code,
        content=response,
    )


# =========================================================
# ERROR RESPONSE
# =========================================================

def error_response(
    message: str,
    code: str = "API_ERROR",
    details: Optional[Any] = None,
    status_code: int = 400,
) -> JSONResponse:
    """
    Create a standardized API error response.

    Example:

    {
        "success": false,
        "message": "Document is required",
        "data": null,
        "error": {
            "code": "DOCUMENT_REQUIRED",
            "details": null
        }
    }
    """

    response = {
        "success": False,
        "message": message,
        "data": None,
        "error": {
            "code": code,
            "details": details,
        },
    }

    return JSONResponse(
        status_code=status_code,
        content=response,
    )


# =========================================================
# VALIDATION ERROR
# =========================================================

def validation_error_response(
    message: str = "Request validation failed",
    details: Optional[Any] = None,
) -> JSONResponse:
    """
    Standard response for invalid incoming requests.
    """

    return error_response(
        message=message,
        code="VALIDATION_ERROR",
        details=details,
        status_code=400,
    )


# =========================================================
# NOT FOUND RESPONSE
# =========================================================

def not_found_response(
    message: str = "Resource not found",
    details: Optional[Any] = None,
) -> JSONResponse:
    """
    Standard response when requested data does not exist.
    """

    return error_response(
        message=message,
        code="NOT_FOUND",
        details=details,
        status_code=404,
    )


# =========================================================
# SERVER ERROR RESPONSE
# =========================================================

def server_error_response(
    message: str = "Internal server error",
    details: Optional[Any] = None,
) -> JSONResponse:
    """
    Standard response for unexpected server errors.
    """

    return error_response(
        message=message,
        code="INTERNAL_SERVER_ERROR",
        details=details,
        status_code=500,
    )