from src.intent.exceptions import IntentErrorCode, IntentException
from src.intent.llm_classify.models import ClassifyIntentLabel
from src.intent.nlu_classify.models import NLUIntentLabel
from src.intent.models import Intent
from src.intent.utils import CaptionLoader, StepsLoader
from src.intent.llm_segment_match.service import IntentSegmentMatchService
from src.intent.nlu_classify.service import IntentNLUClassifyService
from src.intent.llm_classify.service import IntentLLMClassifyService
from src.intent.llm_timer_match.service import IntentTimerMatchService
from src.models import IntentProvider
from src.user_session.recipe.models import RecipeCaption, RecipeStep
from typing import List, Optional
from src.intent.nlu_timer_parse.service import IntentNLUTimerParseService
from uvicorn.main import logger

class NLUService:
    """NLU 기반 인텐트 분석 서비스"""
    
    def __init__(self,
                 nlu_classify_service: IntentNLUClassifyService,
                 nlu_timer_parse_service: IntentNLUTimerParseService):
        self.nlu_classify_service = nlu_classify_service
        self.nlu_timer_parse_service = nlu_timer_parse_service
    
    def analyze_intent(self, text: str) -> Optional[Intent]:
        matched_intent = self.nlu_classify_service.match_intent(text)
        
        if not matched_intent:
            return None
            
        if matched_intent.label == NLUIntentLabel.TIMER_SET:
            timer_time = self.nlu_timer_parse_service.extract_time(text)
            if timer_time:
                return Intent(f"{matched_intent.as_string()} {timer_time}", text, IntentProvider.NLU)
            return None
        
        if matched_intent.label == NLUIntentLabel.WRONG:
            return Intent(NLUIntentLabel.EXTRA.value, text, IntentProvider.NLU)
        
        if matched_intent.label not in [NLUIntentLabel.EXTRA, NLUIntentLabel.TIMER_SET]:
            return Intent(matched_intent.as_string(), text, IntentProvider.NLU)
        
        return None


class LLMService:
    """LLM 기반 인텐트 분석 서비스"""
    
    def __init__(self,
                 classify_service: IntentLLMClassifyService,
                 time_match_service: IntentSegmentMatchService,
                 timer_match_service: IntentTimerMatchService):
        self.classify_service = classify_service
        self.time_match_service = time_match_service
        self.timer_match_service = timer_match_service
    
    def analyze_intent(self, text: str, recipe_captions: List[RecipeCaption], 
                      recipe_steps: List[RecipeStep]) -> Intent:
        classify_intent = self.classify_service.classify_intent(text, len(recipe_steps))
        
        if classify_intent.label == ClassifyIntentLabel.TIMESTAMP:
            timestamp_intent = self.time_match_service.time_match(text, recipe_captions)
            return Intent(timestamp_intent.as_string(), text, IntentProvider.GPT4_1)
        
        elif classify_intent.label == ClassifyIntentLabel.TIMER:
            timer_intent = self.timer_match_service.timer_match(text)
            return Intent(timer_intent.as_string(), text, IntentProvider.GPT4_1)
        elif classify_intent.label == ClassifyIntentLabel.ERROR:
            logger.error(f"[LLMService]: LLM 인텐트 분류 실패: {classify_intent.as_string()}")
            return Intent(ClassifyIntentLabel.EXTRA, text, IntentProvider.GPT4_1)
        else:
            return Intent(classify_intent.as_string(), text, IntentProvider.GPT4_1)


class IntentService:
    """인텐트 분석 서비스"""
    
    def __init__(self,
                 caption_loader: CaptionLoader,
                 steps_loader: StepsLoader,
                 nlu_service: NLUService,
                 llm_service: LLMService):
        self.caption_loader = caption_loader
        self.steps_loader = steps_loader
        self.nlu_service = nlu_service
        self.llm_service = llm_service
    
    async def analyze(self, base_intent: str, recipe_captions: List[RecipeCaption],
                      recipe_steps: List[RecipeStep]) -> Intent:
        try:
            nlu_result = self.nlu_service.analyze_intent(base_intent)
            if nlu_result:
                logger.info(f"[IntentService]: NLU 결과: {nlu_result.intent}")
                return nlu_result
            
            llm_result = self.llm_service.analyze_intent(base_intent, recipe_captions, recipe_steps)
            logger.info(f"[IntentService]: LLM 결과: {llm_result.intent}")
            return llm_result
            
        except IntentException as e:
            logger.error(f"[IntentService]: IntentException 발생 - {e.code.message}")
            raise
        except Exception as e:
            logger.error(f"[IntentService]: 예상치 못한 오류 발생 - {str(e)}")
            raise IntentException(IntentErrorCode.INTENT_SERVICE_ERROR)