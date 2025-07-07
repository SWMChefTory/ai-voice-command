from functools import lru_cache
from src.service import VoiceCommandService
from src.client_session.client import SpringSessionClient
from src.intent.client import GroqClient, SpringIntentClient
from src.intent.utils import CaptionLoader, StepsLoader, PromptGenerator
from src.client_session.repository import SessionRepository, SessionRepositoryImpl
from src.client_session.service import ClientSessionService
from src.stt.client import VitoStreamingClient
from src.stt.repository import STTSessionRepository, STTSessionRepositoryImpl
from src.stt.service import STTService
from src.intent.service import IntentService

@lru_cache
def spring_session_client() -> SpringSessionClient:  
    return SpringSessionClient()

@lru_cache
def groq_client() -> GroqClient:                 
    return GroqClient()

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
def spring_intent_client() -> SpringIntentClient:
    return SpringIntentClient()

@lru_cache
def vito_streaming_client() -> VitoStreamingClient:
    return VitoStreamingClient()

@lru_cache
def stt_repository() -> STTSessionRepository:
    return STTSessionRepositoryImpl()

@lru_cache
def session_repository() -> SessionRepository:
    return SessionRepositoryImpl()

def client_session_service() -> ClientSessionService:
    return ClientSessionService(
        repository      = session_repository(),
        spring_client   = spring_session_client(),
    )

def stt_service() -> STTService:
    return STTService(
        repository    = stt_repository(),
        client = vito_streaming_client(),
    )

def intent_service() -> IntentService:
    return IntentService(
        repository      = session_repository(),
        spring_client   = spring_intent_client(),
        groq_client     = groq_client(),
        caption_loader  = caption_loader(),
        steps_loader    = steps_loader(),
        prompt_generator= prompt_generator(),
    )

def voice_command_service() -> VoiceCommandService:
    return VoiceCommandService(
        stt_service     = stt_service(),
        client_session_service = client_session_service(),
        intent_service  = intent_service(),
    )