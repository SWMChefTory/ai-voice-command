from src.user_session.recipe.models import RecipeCaption
from src.intent.step_match.client import IntentStepMatchClient
from src.intent.step_match.utils import PromptGenerator
from typing import List
from uvicorn.main import logger

class IntentStepMatchService:
    def __init__(self, prompt_generator: PromptGenerator, intent_client: IntentStepMatchClient):
        self.prompt_generator = prompt_generator
        self.intent_client = intent_client

    def step_match(self, intent: str, captions: List[RecipeCaption]) -> str:
        prompt = self.prompt_generator.generate_secondary_system_prompt(captions)
        intent = self.intent_client.request_intent(intent, prompt)
        logger.info(f"[IntentStepMatchService]: 3차 의도 분류 결과: {intent}")
        return intent