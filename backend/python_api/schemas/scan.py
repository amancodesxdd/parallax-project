from typing import Any, Dict, Optional

from pydantic import BaseModel

logger = logging.getLogger(__name__)

logger.info(
    "Scan started: %s",
    scan_id
)


class ScanResponse(BaseModel):
    success: bool
    message: str

    ocr: Optional[Dict[str, Any]] = None
    validation: Optional[Dict[str, Any]] = None
    face: Optional[Dict[str, Any]] = None
    risk: Optional[Dict[str, Any]] = None

    pipeline_status: str