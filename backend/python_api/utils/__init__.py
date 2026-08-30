"""
Utils package initialization.
Exports logging, response formatting, rate limiting, and fallback utilities.
"""

from .logger import setup_logging
from .rate_limiter import RateLimiter
from .response_formatter import error_response, success_response
from .fallback_handler import get_ocr_fallback

__all__ = [
    "setup_logging",
    "RateLimiter",
    "error_response",
    "success_response",
    "get_ocr_fallback",
]