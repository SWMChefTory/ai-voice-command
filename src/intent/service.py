from uvicorn.main import logger
from src.intent.client import IntentClient
from src.intent.exceptions import IntentErrorCode, IntentException
from src.intent.models import Intent
from src.intent.utils import CaptionLoader, StepsLoader, PromptGenerator

class IntentService:
    def __init__(self, 
        intent_client: IntentClient,
        caption_loader: CaptionLoader,
        steps_loader: StepsLoader,
        prompt_generator: PromptGenerator
    ):
        self.intent_client = intent_client
        self.caption_loader = caption_loader
        self.steps_loader = steps_loader
        self.prompt_generator = prompt_generator

    async def analyze(self, base_intent: str) -> Intent:
        try:
            captions = self.caption_loader.load_caption()
            steps = self.steps_loader.load_steps()
            prompt = self.prompt_generator.generate_prompt(captions, steps)
            intent = self.intent_client.request_intent(user_prompt=base_intent, system_prompt=prompt)
            return Intent(intent, base_intent)
        except IntentException as e:
            logger.error(f"[IntentService] {e.code.value}: {e.original_exception}", exc_info=True)
            raise IntentException(IntentErrorCode.INTENT_SERVICE_ERROR, e)
        except Exception as e:
            logger.error(f"[IntentService]: {e}",exc_info=True)
            raise IntentException(IntentErrorCode.INTENT_SERVICE_ERROR, e)