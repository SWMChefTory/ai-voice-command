from functools import lru_cache
from src.service import VoiceCommandService
from src.user_session.client import UserSessionClient, UserSessionClient, UserSessionClientImpl
from src.intent.client import GroqIntentClient, IntentClient
from src.intent.utils import CaptionLoader, StepsLoader, PromptGenerator
from src.stt.client import STTClient, VitoStreamingClient
from src.user_session.repository import UserSessionRepository, UserSessionRepositoryImpl
from src.stt.repository import STTSessionRepository, STTSessionRepositoryImpl
from src.stt.service import STTService
from src.intent.service import IntentService
from src.user_session.service import UserSessionService


@lru_cache
def intent_client() -> IntentClient:                 
    return GroqIntentClient()

@lru_cache
def caption_loader() -> CaptionLoader:           
    return CaptionLoader()

@lru_cache
def steps_loader() -> StepsLoader:               
    return StepsLoader()

@lru_cache
def prompt_generator() -> PromptGenerator:       
    return PromptGenerator()

@lru_cache
def user_session_client() -> UserSessionClient:
    return UserSessionClientImpl()

@lru_cache
def stt_client() -> STTClient:
    return VitoStreamingClient() 

@lru_cache
def stt_repository() -> STTSessionRepository:
    return STTSessionRepositoryImpl()

@lru_cache
def user_session_repository() -> UserSessionRepository:
    return UserSessionRepositoryImpl()

@lru_cache
def user_session_service() -> UserSessionService:
    return UserSessionService(
        repository      = user_session_repository(),
        client   = user_session_client(),
    )

@lru_cache
def stt_service() -> STTService:
    return STTService(
        repository    = stt_repository(),
        client = stt_client(),
    )

@lru_cache
def intent_service() -> IntentService:
    return IntentService(
        intent_client   = intent_client(),
        caption_loader  = caption_loader(),
        steps_loader    = steps_loader(),
        prompt_generator= prompt_generator(),
    )

@lru_cache
def voice_command_service() -> VoiceCommandService:
    return VoiceCommandService(
        stt_service     = stt_service(),
        intent_service  = intent_service(),
        user_session_service = user_session_service(),
    )