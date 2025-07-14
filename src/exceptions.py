from fastapi import HTTPException
from typing import Any, Dict, Optional


class BaseCustomException(Exception):    
    def __init__(
        self,
        message: str = "An error occurred",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(BaseCustomException):    
    def __init__(self, message: str = "Validation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 400, details)


def create_http_exception(custom_exception: BaseCustomException) -> HTTPException:
    return HTTPException(
        status_code=custom_exception.status_code,
        detail={
            "message": custom_exception.message,
            "details": custom_exception.details
        }
    ) 