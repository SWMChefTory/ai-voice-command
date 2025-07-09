from uvicorn.main import logger
from src.intent.client import IntentClient, UserSessionClient
from src.intent.exceptions import IntentErrorCode, IntentException
from src.intent.models import Intent
from src.intent.utils import CaptionLoader, StepsLoader, PromptGenerator
from src.user_session.repository import UserSessionRepository

class IntentService:
    def __init__(self, 
        repository: UserSessionRepository, 
        user_session_client: UserSessionClient, 
        intent_client: IntentClient,
        caption_loader: CaptionLoader,
        steps_loader: StepsLoader,
        prompt_generator: PromptGenerator
    ):
        self.repository = repository
        self.user_session_client = user_session_client
        self.intent_client = intent_client
        self.caption_loader = caption_loader
        self.steps_loader = steps_loader
        self.prompt_generator = prompt_generator

    async def analyze(self, session_id: str, base_intent: str) -> Intent:
        try:
            user_session_websocket = self.repository.get_user_session(session_id)
            captions = self.caption_loader.load_caption()
            steps = self.steps_loader.load_steps()
            prompt = self.prompt_generator.generate_prompt(captions, steps)
            intent = self.intent_client.request_intent(user_prompt=base_intent, system_prompt=prompt)
            return Intent(intent, base_intent)
        except IntentException as e:
            logger.error(f"[IntentService] {e.code.value}: {e.original_exception}", exc_info=True)
            await self.user_session_client.send_error(user_session_websocket, e)
            raise IntentException(IntentErrorCode.INTENT_SERVICE_ERROR, e)
        except Exception as e:
            logger.error(f"[IntentService]: {e}",exc_info=True)
            await self.user_session_client.send_error(user_session_websocket, e)
            raise IntentException(IntentErrorCode.INTENT_SERVICE_ERROR, e)

    async def send_result(self, session_id: str, intent: Intent):
        try:
            user_session_websocket = self.repository.get_user_session(session_id)
            await self.user_session_client.send_intent(user_session_websocket, intent)
        except IntentException as e:
            logger.error(f"[IntentService] {e.code.value}: {e.original_exception}", exc_info=True)
            await self.user_session_client.send_error(user_session_websocket, e)
            raise IntentException(IntentErrorCode.INTENT_SERVICE_ERROR, e)
        except Exception as e:
            logger.error(f"[IntentService]: {e}",exc_info=True)
            await self.user_session_client.send_error(user_session_websocket, e)
            raise IntentException(IntentErrorCode.INTENT_SERVICE_ERROR, e)