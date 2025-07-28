from functools import lru_cache

from src.intent.classify.client import AzureIntentClient, IntentClient
from src.intent.classify.utils import PromptGenerator
from src.intent.step_match.client import AzureIntentStepMatchClient, IntentStepMatchClient
from src.intent.step_match.utils import PromptGenerator as StepMatchPromptGenerator
from src.intent.step_match.service import IntentStepMatchService
from src.intent.pattern_match.service import IntentPatternMatchService
from src.intent.classify.service import IntentClassifyService
from src.service import VoiceCommandService
from src.user_session.client import UserSessionClient, UserSessionClientImpl
from src.intent.utils import CaptionLoader, StepsLoader
from src.stt.client import NaverClovaStreamingClient, OpenAIStreamingClient, VitoStreamingClient
from src.user_session.repository import UserSessionRepository, UserSessionRepositoryImpl
from src.stt.repository import STTSessionRepository, STTSessionRepositoryImpl
from src.stt.service import STTService
from src.intent.service import IntentService
from src.user_session.service import UserSessionService
from src.client import CheftoryVoiceCommandClient, VoiceCommandClient
from src.auth.service import AuthService
from src.auth.client import AuthClient, CheftoryAuthClient
from src.user_session.recipe.service import RecipeService
from src.user_session.recipe.client import RecipeCheftoryClient, RecipeClient

@lru_cache
def auth_client() -> AuthClient:
    return CheftoryAuthClient()

@lru_cache
def voice_command_client() -> VoiceCommandClient:
    return CheftoryVoiceCommandClient()

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
def vito_client() -> VitoStreamingClient:
    return VitoStreamingClient()

@lru_cache
def naver_clova_client() -> NaverClovaStreamingClient:
    return NaverClovaStreamingClient()

@lru_cache
def openai_client() -> OpenAIStreamingClient:
    return OpenAIStreamingClient()

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
def recipe_client() -> RecipeClient:
    return RecipeCheftoryClient()

@lru_cache
def auth_service() -> AuthService:
    return AuthService(auth_client())

@lru_cache
def recipe_service() -> RecipeService:
    return RecipeService(
        client = recipe_client(),
    )

@lru_cache
def user_session_service() -> UserSessionService:
    return UserSessionService(
        recipe_service = recipe_service(),
        repository      = user_session_repository(),
        client   = user_session_client(),
    )

@lru_cache
def stt_service() -> STTService:
    return STTService(
        repository    = stt_repository(),
        naver_clova_client = naver_clova_client(),
        openai_client = openai_client(),
        vito_client = vito_client(),
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
        auth_service = auth_service(),
        voice_command_client = voice_command_client(),
    )