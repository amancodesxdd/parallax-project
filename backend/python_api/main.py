import logging
import time

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from routers.ocr import router as ocr_router
from routers.upload import router as upload_router
from routers.scan import router as scan_router
from routers.face import router as face_router
from routers.validate import router as validate_router
from routers.history import router as history_router
from routers.blacklist import router as blacklist_router

from utils.response_formatter import error_response
from utils.logger import setup_logging
from utils.rate_limiter import RateLimiter

setup_logging()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

rate_limiter = RateLimiter()

app = FastAPI(
    title="AI-Based Fake Identity & Document Screening System",
    description="Backend API Gateway for Passport Forensic & Verification System (SIH 2026)",
    version="1.0.0",
)

# =================================================
# CORS CONFIGURATION
# =================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://*.vercel.app",  # Added for production frontend deployment
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =================================================
# MIDDLEWARE
# =================================================
@app.middleware("http")
async def rate_limit_requests(request: Request, call_next):
    """Limit requests from each client IP."""
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


@app.middleware("http")
async def log_api_requests(request: Request, call_next):
    """Log incoming API request duration and response status."""
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

# =================================================
# HEALTH CHECK
# =================================================
@app.get("/api/health", tags=["System"])
async def health_check():
    return {
        "success": True,
        "status": "ok",
        "message": "SIH backend is running",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }

# =================================================
# EXCEPTION HANDLERS
# =================================================
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Convert FastAPI HTTP errors into standard API format."""
    if isinstance(exc.detail, dict):
        message = exc.detail.get("message", "Request failed")
        code = exc.detail.get("code", "HTTP_ERROR")
        details = exc.detail.get("details")
    else:
        message = str(exc.detail)
        code = "HTTP_ERROR"
        details = None

    return error_response(
        message=message,
        code=code,
        details=details,
        status_code=exc.status_code,
    )


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle invalid API request parameters."""
    return error_response(
        message="Request validation failed",
        code="VALIDATION_ERROR",
        details=exc.errors(),
        status_code=422,
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch unhandled backend errors."""
    logger.exception("Unhandled server error on %s %s", request.method, request.url.path)
    return error_response(
        message="An unexpected server error occurred",
        code="INTERNAL_SERVER_ERROR",
        status_code=500,
    )

# =================================================
# ROUTER INCLUSIONS (WITH API PREFIXES & TAGS)
# =================================================
app.include_router(ocr_router, prefix="/api/ocr", tags=["OCR Extraction"])
app.include_router(upload_router, prefix="/api/upload", tags=["File Upload"])
app.include_router(scan_router, prefix="/api/scan", tags=["Scanning Engine"])
app.include_router(face_router, prefix="/api/face", tags=["Face Matching"])
app.include_router(validate_router, prefix="/api/validate", tags=["Validation Rules"])
app.include_router(history_router, prefix="/api/history", tags=["Scan History"])
app.include_router(blacklist_router, prefix="/api/blacklist", tags=["Blacklist Database"])