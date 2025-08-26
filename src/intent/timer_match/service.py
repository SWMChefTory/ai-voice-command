from src.intent.timer_match.client import IntentTimerMatchClient
from src.intent.timer_match.utils import PromptGenerator
from uvicorn.main import logger

class IntentTimerMatchService:
    def __init__(self, prompt_generator: PromptGenerator, intent_client: IntentTimerMatchClient):
        self.prompt_generator = prompt_generator
        self.intent_client = intent_client

    def timer_match(self, intent: str) -> str:
        prompt = self.prompt_generator.generate_secondary_system_prompt()
        intent = self.intent_client.request_intent(intent, prompt)
        logger.info(f"[IntentTimerMatchService]: 3차 의도 분류 결과: {intent}")
        return intent