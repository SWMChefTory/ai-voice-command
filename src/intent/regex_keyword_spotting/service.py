import re
from src.intent.models import Intent
from src.enums import IntentProvider

class RegexKeywordSpottingService:
    """정규식 기반 웨이크워드('토리야') 단건 탐지"""

    _wakeword_re = re.compile(
            r"(?<![가-힣A-Za-z0-9])(토리야|소리야)(?![가-힣A-Za-z0-9])"
    )
    
    def detect(self, text: str) -> Intent | None:
        """문장에서 첫 번째 '토리야'만 찾음"""
        if not text:
            return None

        m = self._wakeword_re.search(text)
        if not m:
            return None

        return Intent(
            intent="WAKEWORD",
            base_intent=text,
            provider=IntentProvider.REGEX
        )