import logging

logger = logging.getLogger(__name__)


def get_ocr_fallback(reason: str):
    """
    Return mock OCR data when Azure OCR is unavailable.

    This fallback is intended for development,
    integration testing, and temporary external
    service failures.
    """

    logger.warning(
        "OCR fallback activated. Reason: %s",
        reason
    )

    return {
        "provider": "fallback",
        "model": "mock-ocr",
        "filename": None,
        "raw_text": "",
        "fields": {
            "document_type": {
                "value": "passport",
                "confidence": 0.0
            },
            "passport_number": {
                "value": "MOCK123456",
                "confidence": 0.0
            },
            "name": {
                "value": "MOCK USER",
                "confidence": 0.0
            },
            "nationality": {
                "value": "IND",
                "confidence": 0.0
            },
            "date_of_birth": {
                "value": "2000-01-01",
                "confidence": 0.0
            },
            "date_of_expiry": {
                "value": "2030-01-01",
                "confidence": 0.0
            }
        },
        "fallback": True,
        "fallback_reason": reason
    }