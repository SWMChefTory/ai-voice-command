from src.enums import IntentProvider

"""
Intent 모델
intent: 의도파악 결과
base_intent: 의도 파악 전 원본 문자열 (STT 결과)
provider: 의도 파악 제공자
"""
class Intent:
    def __init__(self, intent: str, base_intent: str, provider: IntentProvider):
        self.intent = self._validate_intent(intent)
        self.base_intent = base_intent
        self.provider = provider

    def _validate_intent(self, intent: str) -> str:
        if intent in ["NEXT", "PREV", "EXTRA", "WAKEWORD"]:
            return intent
        elif intent.startswith("STEP") or intent.startswith("TIMESTAMP") or intent.startswith("TIMER") or intent.startswith("VIDEO"):
            return intent
        else:
            return "EXTRA"