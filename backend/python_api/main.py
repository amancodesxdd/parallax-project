import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.ocr import router as ocr_router
from routers.upload import router as upload_router
from routers.scan import router as scan_router
from routers.face import router as face_router
from routers.validate import router as validate_router
from routers.history import router as history_router
from routers.blacklist import router as blacklist_router


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


app.include_router(ocr_router)
app.include_router(upload_router)
app.include_router(scan_router)
app.include_router(face_router)
app.include_router(validate_router)
app.include_router(history_router)
app.include_router(blacklist_router)
