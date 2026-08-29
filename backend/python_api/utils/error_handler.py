import logging
from typing import Any, Optional


logger = logging.getLogger(__name__)


class AppError(Exception):
    """
    Base application error.

    Used for errors that are expected and can be
    safely communicated to the frontend.
    """

    def __init__(
        self,
        message: str,
        code: str,
        status_code: int = 400,
        details: Optional[Any] = None,
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details

        super().__init__(message)


class OCRServiceError(AppError):
    """Raised when OCR processing fails."""

    def __init__(
        self,
        message: str = "OCR processing failed",
        details: Optional[Any] = None,
    ):
        super().__init__(
            message=message,
            code="OCR_FAILED",
            status_code=502,
            details=details,
        )


class FaceServiceError(AppError):
    """Raised when face verification fails."""

    def __init__(
        self,
        message: str = "Face verification failed",
        details: Optional[Any] = None,
    ):
        super().__init__(
            message=message,
            code="FACE_VERIFICATION_FAILED",
            status_code=502,
            details=details,
        )


class DocumentValidationError(AppError):
    """Raised when document validation fails."""

    def __init__(
        self,
        message: str = "Document validation failed",
        details: Optional[Any] = None,
    ):
        super().__init__(
            message=message,
            code="DOCUMENT_VALIDATION_FAILED",
            status_code=422,
            details=details,
        )


class StorageServiceError(AppError):
    """Raised when file storage fails."""

    def __init__(
        self,
        message: str = "File storage operation failed",
        details: Optional[Any] = None,
    ):
        super().__init__(
            message=message,
            code="STORAGE_FAILED",
            status_code=502,
            details=details,
        )


def log_error(
    message: str,
    exception: Exception,
) -> None:
    """
    Log technical error details on the backend.

    Detailed internal information should stay in
    backend logs and should not be exposed to the frontend.
    """

    logger.exception(
        "%s: %s",
        message,
        exception,
    )