from enum import Enum

class VoiceCommandErrorCode(Enum):
    VOICE_COMMAND_SERVICE_ERROR = "음성 명령 서비스 오류"

class BusinessException(Exception):
    def __init__(self, code: Enum):
        self.code = code

class VoiceCommandException(BusinessException):
    def __init__(self, code: Enum):
        super().__init__(code)
        self.code = code