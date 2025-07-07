from enum import Enum

from src.exceptions import VoiceCommandException


class IntentErrorCode(Enum):
    GROQ_REQUEST_SEND_ERROR = "Groq API 요청 전송 실패했습니다."
    SPRING_INTENT_SEND_ERROR = "Spring으로 의도 파악 결과를 보내는데 실패했습니다."
    CAPTION_LOAD_ERROR = "자막을 로드하는데 실패했습니다."
    STEPS_LOAD_ERROR = "스텝을 로드하는데 실패했습니다."
    INTENT_SERVICE_ERROR = "의도 파악 서비스에 오류가 발생했습니다."


class IntentException(VoiceCommandException):
    def __init__(self, code: IntentErrorCode, original_exception: Exception):
        super().__init__(code, original_exception)
        self.code = code
        self.original_exception = original_exception
        
class _GroqClientException(IntentException):
    def __init__(self, code: IntentErrorCode, original_exception: Exception):
        super().__init__(code, original_exception)

class _SpringIntentClientException(IntentException):
    def __init__(self, code: IntentErrorCode, original_exception: Exception):
        super().__init__(code, original_exception)

class _CaptionLoaderException(IntentException):
    def __init__(self, code: IntentErrorCode, original_exception: Exception):
        super().__init__(code, original_exception)

class _StepsLoaderException(IntentException):
    def __init__(self, code: IntentErrorCode, original_exception: Exception):
        super().__init__(code, original_exception)