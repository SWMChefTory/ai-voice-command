from enum import Enum
from src.exceptions import VoiceCommandException


class SessionErrorCode(Enum):
    SESSION_SERVICE_ERROR = ("SESSION_1", "세션 서비스에 오류가 발생했습니다.")
    SESSION_NOT_FOUND = ("SESSION_2", "세션을 찾을 수 없습니다.")

    def __init__(self, code: str, message: str):
        self._code = code
        self._message = message

    @property
    def code(self) -> str:
        return self._code

    @property
    def message(self) -> str:
        return self._message


class SessionException(VoiceCommandException):
    def __init__(self, code: SessionErrorCode):
        super().__init__(code)
        self.code = code