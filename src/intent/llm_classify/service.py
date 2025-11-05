from src.intent.llm_classify.utils import PromptGenerator
from src.intent.llm_classify.client import IntentClassifyClient, LLMClassifyResult

class IntentLLMClassifyService():
    def __init__(self, prompt_generator: PromptGenerator, intent_client: IntentClassifyClient):
        self.prompt_generator = prompt_generator
        self.intent_client = intent_client

    def classify_intent(self, user_prompt: str, total_steps: int) -> LLMClassifyResult:
        prompt = self.prompt_generator.generate_prompt(total_steps)
        return self.intent_client.request_intent(user_prompt, prompt, total_steps)