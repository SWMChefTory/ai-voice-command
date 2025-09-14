from abc import ABC, abstractmethod
import httpx
from uvicorn.main import logger
from src.intent.models import Intent
from src.enums import STTProvider
from src.schemas import VoiceCommandRequest
from .config import voice_command_config
from uuid import UUID

class VoiceCommandClient(ABC):
    @abstractmethod
    async def send_result(self, stt_provider: STTProvider, result: Intent, user_id: UUID, session_id: str, start: int, end: int):
        pass

class CheftoryVoiceCommandClient(VoiceCommandClient):

    def __init__(self):
        self.config = voice_command_config

    async def send_result(self, stt_provider: STTProvider, result: Intent, user_id: UUID, session_id: str, start: int, end: int):
        url = f"{self.config.api_base}/papi/v1/voice-command"
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                url,
                json=VoiceCommandRequest.from_intent(result, user_id, stt_provider, session_id, start, end).model_dump()
            )
        except Exception as e:
            logger.error(e, exc_info=True)