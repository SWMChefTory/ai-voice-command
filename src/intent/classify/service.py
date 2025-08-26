from src.intent.classify.utils import PromptGenerator
from src.intent.classify.client import IntentClient
from uvicorn.main import logger
class IntentClassifyService():
    def __init__(self, prompt_generator: PromptGenerator, intent_client: IntentClient):
        self.prompt_generator = prompt_generator
        self.intent_client = intent_client

    def classify_intent(self, intent: str, total_steps: int) -> str:
        prompt = self.prompt_generator.generate_prompt(total_steps)
        intent = self.intent_client.request_intent(intent, prompt, total_steps)
        logger.info(f"[IntentClassifyService]: 2차 의도 분류 결과: {intent}")
        return intent