from enum import Enum

from src.exceptions import VoiceCommandException

class AuthErrorCode(Enum):
    INVALID_TOKEN = ("AUTH_1", "유효하지 않은 토큰입니다.")
    EXPIRED_TOKEN = ("AUTH_2", "만료된 토큰입니다.")
    INVALID_USER = ("AUTH_3", "유효하지 않은 사용자입니다.")

    def __init__(self, code: str, message: str):
        self._code = code
        self._message = message

    @property
    def code(self) -> str:
        return self._code

    @property
    def message(self) -> str:
        return self._message

class AuthException(VoiceCommandException):
    def __init__(self, code: AuthErrorCode):
        super().__init__(code)
        self.code = code
