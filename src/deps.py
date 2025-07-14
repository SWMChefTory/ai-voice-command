from functools import lru_cache

from src.intent.classify.client import AzureIntentClient, IntentClient
from src.intent.classify.utils import PromptGenerator
from src.intent.step_match.client import AzureIntentStepMatchClient, IntentStepMatchClient
from src.intent.step_match.utils import PromptGenerator as StepMatchPromptGenerator
from src.intent.step_match.service import IntentStepMatchService
from src.intent.pattern_match.service import IntentPatternMatchService
from src.intent.classify.service import IntentClassifyService
from src.service import VoiceCommandService
from src.user_session.client import UserSessionClient, UserSessionClient, UserSessionClientImpl
from src.intent.utils import CaptionLoader, StepsLoader
from src.stt.client import STTClient, VitoStreamingClient
from src.user_session.repository import UserSessionRepository, UserSessionRepositoryImpl
from src.stt.repository import STTSessionRepository, STTSessionRepositoryImpl
from src.stt.service import STTService
from src.intent.service import IntentService
from src.user_session.service import UserSessionService


@lru_cache
def intent_client() -> IntentClient:                 
    return AzureIntentClient()

@lru_cache
def intent_step_match_client() -> IntentStepMatchClient:
    return AzureIntentStepMatchClient()

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
def step_match_prompt_generator() -> StepMatchPromptGenerator:
    return StepMatchPromptGenerator()

@lru_cache
def intent_step_match_service() -> IntentStepMatchService:
    return IntentStepMatchService(
        prompt_generator = step_match_prompt_generator(),
        intent_client = intent_step_match_client(),
    )

@lru_cache
def intent_pattern_match_service() -> IntentPatternMatchService:
    return IntentPatternMatchService()

@lru_cache
def intent_classify_service() -> IntentClassifyService:
    return IntentClassifyService(
        intent_client = intent_client(),
        prompt_generator = prompt_generator(),
    )

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
        caption_loader  = caption_loader(),
        steps_loader    = steps_loader(),
        intent_step_match_service = intent_step_match_service(),
        intent_pattern_match_service = intent_pattern_match_service(),
        intent_classify_service = intent_classify_service(),
    )

@lru_cache
def voice_command_service() -> VoiceCommandService:
    return VoiceCommandService(
        stt_service     = stt_service(),
        intent_service  = intent_service(),
        user_session_service = user_session_service(),
    )