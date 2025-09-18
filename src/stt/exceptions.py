from enum import Enum

from src.exceptions import VoiceCommandException


class STTErrorCode(Enum):
    STT_SERVICE_ERROR = ("STT_1", "STT 서비스에 오류가 발생했습니다.")
    STT_STREAM_ERROR = ("STT_2", "STT 스트리밍에 오류가 발생했습니다.")
    STT_CONNECTION_ERROR = ("STT_3", "STT 연결에 오류가 발생했습니다.")

    def __init__(self, code: str, message: str):
        self._code = code
        self._message = message

    @property
    def code(self) -> str:
        return self._code

    @property
    def message(self) -> str:
        return self._message

class STTException(VoiceCommandException):
    def __init__(self, code: STTErrorCode):
        super().__init__(code)
        self.code = code

class VitoStreamingClientException(STTException):
    def __init__(self, code: STTErrorCode):
        super().__init__(code)

class NaverClovaStreamingClientException(STTException):
    def __init__(self, code: STTErrorCode):
        super().__init__(code)

class OpenAIStreamingClientException(STTException):
    def __init__(self, code: STTErrorCode):
        super().__init__(code)