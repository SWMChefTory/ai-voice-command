from src.models import IntentProvider

class Intent:
    def __init__(self, intent: str, base_intent: str, provider: IntentProvider):
        self.intent = self._validate_intent(intent)
        self.base_intent = base_intent
        self.provider = provider

    def _validate_intent(self, intent: str) -> str:
        if intent in ["NEXT", "PREV", "EXTRA"]:
            return intent
        elif intent.startswith("STEP") or intent.startswith("TIMESTAMP"):
            return intent
        else:
            return "EXTRA"