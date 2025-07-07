from enum import Enum


class VoiceCommandErrorCode(Enum):
    VOICE_COMMAND_SERVICE_ERROR = "음성 명령 서비스 오류"

class BusinessException(Exception):
    def __init__(self, code: Enum, original_exception: Exception):
        self.code = code
        self.original_exception = original_exception

class VoiceCommandException(BusinessException):
    def __init__(self, code: Enum, original_exception: Exception):
        super().__init__(code, original_exception)
        self.code = code
        self.original_exception = original_exception