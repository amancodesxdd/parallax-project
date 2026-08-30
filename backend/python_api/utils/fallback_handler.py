def get_ocr_fallback(reason: str = "OCR service degraded") -> dict:
    """Generates a structured fallback response if OCR engine throws an exception."""
    return {
        "provider": "tesseract-ocr-fallback",
        "raw_text": "SAMPLE PASSPORT TEXT FOR OFFLINE DEMO",
        "fields": {
            "DocumentNumber": {"value": "J1234567", "confidence": 0.50},
            "CountryRegion": {"value": "IND", "confidence": 0.50},
        },
        "fallback": True,
        "fallback_reason": reason,
    }