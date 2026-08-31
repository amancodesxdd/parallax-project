import logging
import time

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from routers import (
    face_router,
    ocr_router,
    upload_router,
)
from utils.logger import setup_logging
from utils.rate_limiter import RateLimiter
from utils.response_formatter import error_response

setup_logging()
logger = logging.getLogger(__name__)

rate_limiter = RateLimiter()

app = FastAPI(
    title="AI-Based Fake Identity & Document Screening System",
    description="Backend API Gateway for Passport Forensic & Verification System (SIH 2026)",
    version="1.0.0",
)

# CORS MIDDLEWARE
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# RATE LIMIT MIDDLEWARE
@app.middleware("http")
async def rate_limit_requests(request: Request, call_next):
    client_id = request.client.host if request.client else "unknown"

    if not rate_limiter.is_allowed(client_id):
        retry_after = rate_limiter.get_retry_after(client_id)
        return JSONResponse(
            status_code=429,
            content={
                "success": False,
                "message": "Too many requests. Please try again later.",
                "error": {
                    "code": "RATE_LIMIT_EXCEEDED",
                    "retry_after": retry_after,
                },
            },
            headers={"Retry-After": str(retry_after)},
        )

    return await call_next(request)


# LOGGING MIDDLEWARE
@app.middleware("http")
async def log_api_requests(request: Request, call_next):
    start_time = time.perf_counter()
    logger.info("API request: %s %s", request.method, request.url.path)

    try:
        response = await call_next(request)
        elapsed_time = time.perf_counter() - start_time
        logger.info(
            "API response: %s %s | status=%s | time=%.3fs",
            request.method,
            request.url.path,
            response.status_code,
            elapsed_time,
        )
        return response
    except Exception:
        elapsed_time = time.perf_counter() - start_time
        logger.exception(
            "API failed: %s %s | time=%.3fs",
            request.method,
            request.url.path,
            elapsed_time,
        )
        raise


# HEALTH ROUTE
@app.get("/api/health", tags=["System"])
async def health_check():
    return {
        "success": True,
        "status": "ok",
        "message": "SIH backend service is operational",
    }


# EXCEPTION HANDLERS
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if isinstance(exc.detail, dict):
        message = exc.detail.get("message", "Request failed")
        code = exc.detail.get("code", "HTTP_ERROR")
        details = exc.detail.get("details")
    else:
        message = str(exc.detail)
        code = "HTTP_ERROR"
        details = None

    return error_response(
        message=message, code=code, details=details, status_code=exc.status_code
    )


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    return error_response(
        message="Request validation failed",
        code="VALIDATION_ERROR",
        details=exc.errors(),
        status_code=422,
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(
        "Unhandled server error on %s %s", request.method, request.url.path
    )
    return error_response(
        message="An unexpected server error occurred",
        code="INTERNAL_SERVER_ERROR",
        status_code=500,
    )


# ROUTER INCLUSIONS (forensic engine only; /api/scan, validation, blacklist,
# and history are served exclusively by the Node gateway server.js)
app.include_router(ocr_router, prefix="/api/ocr", tags=["OCR Extraction"])
app.include_router(face_router, prefix="/api/face", tags=["Face Matching"])
app.include_router(upload_router, prefix="/api/upload", tags=["File Upload"])