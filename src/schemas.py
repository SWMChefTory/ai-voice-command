from typing import Generic, Optional, TypeVar
from uuid import UUID
from pydantic import BaseModel
from src.exceptions import BusinessException
from src.intent.models import Intent
from src.enums import STTProvider

T = TypeVar("T")


class CommonResponse(BaseModel, Generic[T]):
    status: int
    data: Optional[T] = None


class SuccessResponse(CommonResponse[T]):
    def __init__(self, data: Optional[T] = None):
        super().__init__(status=200, data=data)


class IntervalErrorResponse(CommonResponse[dict[str, str]]):
    def __init__(self, error: Exception):
        super().__init__(
            status=500,
            data={"error": str(error)}
        )

class BusinessErrorResponse(CommonResponse[dict[str, str]]):
    def __init__(self, error: BusinessException):
        super().__init__(
            status=400,
            data={
                "code": error.code.name,
                "description": error.code.value
            }
        )
        
class VoiceCommandRequest(BaseModel):
    stt_model: str
    intent_model: str
    transcribe: str
    intent: str
    user_id: str
    audio_file_name: str
    
    @classmethod
    def from_intent(cls, intent: Intent, user_id: UUID, stt_provider: STTProvider, audio_file_name: str) -> "VoiceCommandRequest":
        return cls(
            stt_model=stt_provider.value,
            intent_model=intent.provider.value,
            transcribe=intent.base_intent,
            intent=intent.intent,
            user_id=str(user_id),
            audio_file_name=audio_file_name
        )