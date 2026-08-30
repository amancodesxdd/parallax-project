"""
Routers package initialization.
Exports all API routers for clean inclusion in main.py.
"""

from .blacklist import router as blacklist_router
from .face import router as face_router
from .history import router as history_router
from .ocr import router as ocr_router
from .scan import router as scan_router
from .upload import router as upload_router
from .validate import router as validate_router

__all__ = [
    "blacklist_router",
    "face_router",
    "history_router",
    "ocr_router",
    "scan_router",
    "upload_router",
    "validate_router",
]