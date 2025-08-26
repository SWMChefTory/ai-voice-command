from src.user_session.recipe.models import RecipeCaption
from src.intent.time_match.client import IntentTimeMatchClient
from src.intent.time_match.utils import PromptGenerator
from typing import List
from uvicorn.main import logger

class IntentTimeMatchService:
    def __init__(self, prompt_generator: PromptGenerator, intent_client: IntentTimeMatchClient):
        self.prompt_generator = prompt_generator
        self.intent_client = intent_client

    def time_match(self, intent: str, captions: List[RecipeCaption]) -> str:
        prompt = self.prompt_generator.generate_secondary_system_prompt(captions)
        intent = self.intent_client.request_intent(intent, prompt)
        logger.info(f"[IntentTimeMatchService]: 3차 의도 분류 결과: {intent}")
        return intent