from src.intent.llm_timer_match.client import IntentTimerMatchClient
from src.intent.llm_timer_match.utils import PromptGenerator
from src.intent.llm_timer_match.models import TimerIntentResult

class IntentTimerMatchService:
    def __init__(self, prompt_generator: PromptGenerator, intent_client: IntentTimerMatchClient):
        self.prompt_generator = prompt_generator
        self.intent_client = intent_client

    def timer_match(self, intent: str) -> TimerIntentResult:
        prompt = self.prompt_generator.generate_secondary_system_prompt()
        return self.intent_client.request_intent(intent, prompt)