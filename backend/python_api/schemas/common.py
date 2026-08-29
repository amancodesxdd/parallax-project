from typing import Any, Optional

from pydantic import BaseModel


class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None


class ValidateRequest(BaseModel):
    passport_number: str
    name: str
    nationality: str
    date_of_birth: str
    date_of_expiry: str


class BlacklistRequest(BaseModel):
    document_number: str
    reason: str
