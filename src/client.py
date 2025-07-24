from abc import ABC, abstractmethod
import httpx
from uvicorn.main import logger
from src.intent.models import Intent
from src.models import STTProvider
from src.schemas import VoiceCommandResponse
from .config import voice_command_config
from uuid import UUID

class VoiceCommandClient(ABC):
    @abstractmethod
    async def send_result(self, stt_provider: STTProvider, result: Intent, user_id: UUID):
        pass

class CheftoryVoiceCommandClient(VoiceCommandClient):

    def __init__(self):
        self.config = voice_command_config

    async def send_result(self, stt_provider: STTProvider, result: Intent, user_id: UUID):
        url = f"{self.config.api_base}/papi/v1/voice-command"
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                url,
                json=VoiceCommandResponse.from_intent(result, user_id, stt_provider).model_dump()
            )
        except Exception as e:
            logger.error(e, exc_info=True)