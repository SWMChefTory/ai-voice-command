from typing import Generic, Optional, TypeVar
from pydantic import BaseModel
from src.exceptions import BusinessException

T = TypeVar("T")


class CommonResponse(BaseModel, Generic[T]):
    status: int
    data: Optional[T] = None


class SuccessResponse(CommonResponse[T]):
    def __init__(self, data: Optional[T] = None):
        super().__init__(status=200, data=data)


class IntervalErrorResponse(CommonResponse[dict]):
    def __init__(self, error: Exception):
        super().__init__(
            status=500,
            data={"error": str(error)}
        )


class BusinessErrorResponse(CommonResponse[dict]):
    def __init__(self, error: BusinessException):
        super().__init__(
            status=400,
            data={
                "code": error.code.name,
                "description": error.code.value
            }
        )