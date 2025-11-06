
from typing import List

from src.intent.llm_ingredient_match.client import IntentIngredientMatchClient
from src.intent.llm_ingredient_match.models import LLMIngredientMatchResult
from src.intent.llm_ingredient_match.utils import IngredientMatchPromptGenerator
from src.user_session.recipe.models import RecipeIngredient


class IntentIngredientMatchService:
    def __init__(self, prompt_generator: IngredientMatchPromptGenerator, intent_client: IntentIngredientMatchClient):
        self.prompt_generator = prompt_generator
        self.intent_client = intent_client

    def ingredient_match(self, intent: str, ingredients: List[RecipeIngredient]) -> LLMIngredientMatchResult:
        prompt = self.prompt_generator.generate_secondary_system_prompt(ingredients)
        return self.intent_client.request_intent(intent, prompt)