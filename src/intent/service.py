from uvicorn.main import logger
from src.intent.client import GroqClient, SpringIntentClient
from src.intent.exceptions import IntentErrorCode, IntentException
from src.intent.utils import CaptionLoader, StepsLoader, PromptGenerator
from src.client_session.repository import SessionRepository

class IntentService:
    def __init__(self, 
        repository: SessionRepository, 
        spring_client: SpringIntentClient, 
        groq_client: GroqClient,
        caption_loader: CaptionLoader,
        steps_loader: StepsLoader,
        prompt_generator: PromptGenerator
    ):
        self.repository = repository
        self.spring_client = spring_client
        self.groq_client = groq_client
        self.caption_loader = caption_loader
        self.steps_loader = steps_loader
        self.prompt_generator = prompt_generator

    async def get_intent(self, session_id: str, text: str) -> str:
        try:
            spring_ws = self.repository.get_user_session(session_id)
            caption = self.caption_loader.load_caption()
            steps = self.steps_loader.load_steps()
            prompt = self.prompt_generator.generate_prompt(caption, steps)
            intent = self.groq_client.send_prompt(user_prompt=text, system_prompt=prompt)
            return intent
        except IntentException as e:
            logger.error(f"[IntentService] {e.code.value}: {e.original_exception}", exc_info=True)
            await self.spring_client.send_error(spring_ws, e)
            raise IntentException(IntentErrorCode.INTENT_SERVICE_ERROR, e)
        except Exception as e:
            logger.error(f"[IntentService]: {e}",exc_info=True)
            await self.spring_client.send_error(spring_ws, e)
            raise IntentException(IntentErrorCode.INTENT_SERVICE_ERROR, e)

    async def send_intent(self, session_id: str, intent: str, base_intent: str):
        try:
            spring_ws = self.repository.get_user_session(session_id)
            await self.spring_client.send_intent(spring_ws, intent, base_intent)
        except IntentException as e:
            logger.error(f"[IntentService] {e.code.value}: {e.original_exception}", exc_info=True)
            await self.spring_client.send_error(spring_ws, e)
            raise IntentException(IntentErrorCode.INTENT_SERVICE_ERROR, e)
        except Exception as e:
            logger.error(f"[IntentService]: {e}",exc_info=True)
            await self.spring_client.send_error(spring_ws, e)
            raise IntentException(IntentErrorCode.INTENT_SERVICE_ERROR, e)