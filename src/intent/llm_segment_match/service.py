from src.user_session.recipe.models import RecipeCaption
from src.intent.llm_segment_match.client import IntentTimeMatchClient
from src.intent.llm_segment_match.utils import PromptGenerator
from typing import List
from src.intent.llm_segment_match.models import TimeIntentResult

class IntentSegmentMatchService:
    def __init__(self, prompt_generator: PromptGenerator, intent_client: IntentTimeMatchClient):
        self.prompt_generator = prompt_generator
        self.intent_client = intent_client

    def time_match(self, intent: str, captions: List[RecipeCaption]) -> TimeIntentResult:
        prompt = self.prompt_generator.generate_secondary_system_prompt(captions)
        return self.intent_client.request_intent(intent, prompt)