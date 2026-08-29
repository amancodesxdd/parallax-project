import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from routers.ocr import router as ocr_router
from routers.upload import router as upload_router
from routers.scan import router as scan_router
from routers.face import router as face_router
from routers.validate import router as validate_router
from routers.history import router as history_router
from routers.blacklist import router as blacklist_router

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from utils.response_formatter import error_response


logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="AI-Based Fake Identity & Document Screening System",
    version="1.0.0",
)


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


@app.get("/api/health", tags=["System"])
async def health_check():
    return {
        "success": True,
        "status": "ok",
        "message": "SIH backend is running",
    }

@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    return error_response(
        message="Request validation failed",
        code="VALIDATION_ERROR",
        details=exc.errors(),
        status_code=422,
    )


@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception,
):
    return error_response(
        message="Internal server error",
        code="INTERNAL_SERVER_ERROR",
        status_code=500,
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException,
):
    return error_response(
        message=str(exc.detail),
        code="HTTP_ERROR",
        status_code=exc.status_code,
    )

app.include_router(ocr_router)
app.include_router(upload_router)
app.include_router(scan_router)
app.include_router(face_router)
app.include_router(validate_router)
app.include_router(history_router)
app.include_router(blacklist_router)
