from pydantic import BaseModel
from src.intent.models import Intent

class UserSessionResponse(BaseModel):
    intent: str
    base_intent: str
    start: int
    end: int

    @classmethod
    def from_result(cls, intent: Intent, start: int, end: int) -> "UserSessionResponse":
        return cls(
            intent=intent.intent,
            base_intent=intent.base_intent,
            start=start,
            end=end,
        )