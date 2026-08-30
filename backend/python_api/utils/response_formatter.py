from fastapi.responses import JSONResponse


def success_response(data: dict = None, message: str = "Success", status_code: int = 200):
    return JSONResponse(
        status_code=status_code,
        content={
            "success": True,
            "message": message,
            "data": data or {},
        },
    )


def error_response(
    message: str = "Error",
    code: str = "ERROR",
    details: list | dict = None,
    status_code: int = 400,
):
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "message": message,
            "error": {
                "code": code,
                "details": details,
            },
        },
    )