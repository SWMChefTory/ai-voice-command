import os
from pydantic import BaseModel

class GroqConfig(BaseModel):
    api_key: str = os.getenv("GROQ_API_KEY") or ""
    model: str = "llama-3.1-8b-instant"

groq_config = GroqConfig()