from typing import Any, Dict, Optional

from pydantic import BaseModel


class OCRField(BaseModel):
    value: Optional[Any] = None
    confidence: Optional[float] = None


class OCRResult(BaseModel):
    provider: str
    model: str
    filename: str
    raw_text: str
    fields: Dict[str, OCRField]