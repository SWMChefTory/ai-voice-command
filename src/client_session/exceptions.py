from enum import Enum
from src.exceptions import VoiceCommandException


class SessionErrorCode(Enum):
    SESSION_SERVICE_ERROR = "세션 서비스 오류"

class SessionException(VoiceCommandException):
    def __init__(self, code: SessionErrorCode, original_exception: Exception):
        super().__init__(code, original_exception)
        self.code = code
        self.original_exception = original_exception