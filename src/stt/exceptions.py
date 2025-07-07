from enum import Enum

from src.exceptions import VoiceCommandException


class STTErrorCode(Enum):
    STT_SERVICE_ERROR = "STT 서비스 오류"
    STT_STREAM_ERROR = "STT 스트리밍 오류"
    STT_CONNECTION_ERROR = "STT 연결 오류"


class STTException(VoiceCommandException):
    def __init__(self, code: STTErrorCode, original_exception: Exception):
        super().__init__(code, original_exception)
        self.code = code
        self.original_exception = original_exception

class _VitoStreamingClientException(STTException):
    def __init__(self, code: STTErrorCode, original_exception: Exception):
        super().__init__(code, original_exception)