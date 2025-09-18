from pydantic import BaseModel
from src.intent.models import Intent

class UserSessionResponse(BaseModel):
    intent: str
    base_intent: str

    @classmethod
    def from_result(cls, intent: Intent) -> "UserSessionResponse":
        return cls(
            intent=intent.intent,
            base_intent=intent.base_intent,
        )