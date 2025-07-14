from pydantic import BaseModel

from src.intent.models import Intent

class IntentResponse(BaseModel):
    intent: str
    base_intent: str

    @classmethod
    def from_intent(cls, intent: Intent) -> "IntentResponse":
        return cls(
            intent=intent.intent,
            base_intent=intent.base_intent,
        )