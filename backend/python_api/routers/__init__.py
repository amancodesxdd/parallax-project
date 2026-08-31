"""
Routers package initialization.
Exports all API routers for clean inclusion in main.py.
"""

from .face import router as face_router
from .ocr import router as ocr_router
from .upload import router as upload_router

__all__ = [
    "face_router",
    "ocr_router",
    "upload_router",
]