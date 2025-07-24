from enum import Enum

from src.exceptions import VoiceCommandException


class IntentErrorCode(Enum):
    AZURE_REQUEST_SEND_ERROR = ("INTENT_1", "Azure API 요청 전송에 실패했습니다.")
    SPRING_INTENT_SEND_ERROR = ("INTENT_2", "Spring으로 의도 파악 결과 전송에 실패했습니다.")
    CAPTION_LOAD_ERROR = ("INTENT_3", "자막 로드에 실패했습니다.")
    STEPS_LOAD_ERROR = ("INTENT_4", "스텝 로드에 실패했습니다.")
    INTENT_SERVICE_ERROR = ("INTENT_5", "의도 파악 서비스에서 오류가 발생했습니다.")

    def __init__(self, code: str, message: str):
        self._code = code
        self._message = message

    @property
    def code(self) -> str:
        return self._code

    @property
    def message(self) -> str:
        return self._message


class IntentException(VoiceCommandException):
    def __init__(self, code: IntentErrorCode):
        super().__init__(code)
        self.code = code
        
class AzureClientException(IntentException):
    def __init__(self, code: IntentErrorCode):
        super().__init__(code)

class SpringIntentClientException(IntentException):
    def __init__(self, code: IntentErrorCode):
        super().__init__(code)

class CaptionLoaderException(IntentException):
    def __init__(self, code: IntentErrorCode):
        super().__init__(code)

class StepsLoaderException(IntentException):
    def __init__(self, code: IntentErrorCode):
        super().__init__(code)