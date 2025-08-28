from functools import lru_cache

from src.intent.llm_classify.client import AzureIntentClient, IntentClient
from src.intent.llm_classify.utils import PromptGenerator
from src.intent.llm_timer_match.client import AzureIntentTimerMatchClient, IntentTimerMatchClient
from src.intent.llm_segment_match.client import AzureIntentTimeMatchClient, IntentTimeMatchClient
from src.intent.llm_segment_match.utils import PromptGenerator as TimeMatchPromptGenerator
from src.intent.llm_timer_match.utils import PromptGenerator as TimerMatchPromptGenerator
from src.intent.llm_segment_match.service import IntentSegmentMatchService
from src.intent.nlu_classify.service import IntentNLUClassifyService
from src.intent.llm_classify.service import IntentLLMClassifyService
from src.intent.llm_timer_match.service import IntentTimerMatchService
from src.service import VoiceCommandService
from src.user_session.client import UserSessionClient, UserSessionClientImpl
from src.stt.client import NaverClovaStreamingClient, OpenAIStreamingClient, VitoStreamingClient
from src.user_session.repository import UserSessionRepository, UserSessionRepositoryImpl
from src.stt.repository import STTSessionRepository, STTSessionRepositoryImpl
from src.stt.service import STTService
from src.intent.service import IntentService, NLUService, LLMService
from src.user_session.service import UserSessionService
from src.client import CheftoryVoiceCommandClient, VoiceCommandClient
from src.auth.service import AuthService
from src.auth.client import AuthClient, CheftoryAuthClient
from src.user_session.recipe.service import RecipeService
from src.user_session.recipe.client import RecipeCheftoryClient, RecipeClient
from src.intent.nlu_timer_extract.service import IntentNLUTimerExtractService

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
def intent_time_match_client() -> IntentTimeMatchClient:
    return AzureIntentTimeMatchClient()

@lru_cache
def intent_timer_match_client() -> IntentTimerMatchClient:
    return AzureIntentTimerMatchClient()

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
def time_match_prompt_generator() -> TimeMatchPromptGenerator:
    return TimeMatchPromptGenerator()

@lru_cache
def timer_match_prompt_generator() -> TimerMatchPromptGenerator:
    return TimerMatchPromptGenerator()

@lru_cache
def intent_time_match_service() -> IntentSegmentMatchService:
    return IntentSegmentMatchService(
        prompt_generator = time_match_prompt_generator(),
        intent_client = intent_time_match_client(),
    )

@lru_cache
def intent_nlu_classify_service() -> IntentNLUClassifyService:
    return IntentNLUClassifyService()

@lru_cache
def intent_classify_service() -> IntentLLMClassifyService:
    return IntentLLMClassifyService(
        intent_client = intent_client(),
        prompt_generator = prompt_generator(),
    )

@lru_cache
def intent_timer_match_service() -> IntentTimerMatchService:
    return IntentTimerMatchService(
        prompt_generator = timer_match_prompt_generator(),
        intent_client = intent_timer_match_client(),
    )

@lru_cache
def intent_nlu_timer_parse_service() -> IntentNLUTimerExtractService:
    return IntentNLUTimerExtractService()

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
def nlu_service() -> NLUService:
    return NLUService(
        nlu_classify_service = intent_nlu_classify_service(),
        nlu_timer_parse_service = intent_nlu_timer_parse_service(),
    )

@lru_cache
def llm_service() -> LLMService:
    return LLMService(
        classify_service = intent_classify_service(),
        time_match_service = intent_time_match_service(),
        timer_match_service = intent_timer_match_service(),
    )

@lru_cache
def intent_service() -> IntentService:
    return IntentService(
        nlu_service = nlu_service(),
        llm_service = llm_service(),
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