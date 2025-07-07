from pydantic import BaseModel

class IntentResponse(BaseModel):
    intent: str
    base_intent: str